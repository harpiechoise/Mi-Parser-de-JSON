from dataclasses import dataclass
from pprint import pprint
import string
import sys
import typing


TT_OBJECT_END     = -2
TT_OBJECT_START   = -1
TT_NUMBER         = 1
TT_STRING         = 2
TT_BOOL           = 4
TT_NULL           = 5
TT_LPAREN         = 6
TT_RPAREN         = 7
TT_COMMA          = 8
TT_TUPLE_OPERATOR = 9

@dataclass
class Token:
    type: int
    value: str

class Lexer:
    def __init__(self, input_string: str) -> None:
        # The input string is a string representing a JSON Object
        self.input_string = input_string
        # Index increments by one on call of the __advance method
        self.idx = 0
        # The las character is the las index in the string
        self.last_character = len(input_string)-1
        # Tokens!
        self.token = []
        # Point count to raise malformed floating point numbers
        self.point_count = 0

        self.lex()
        
    def advance(self):
        # If the Index error is raised, we stop reading the string
        if self.idx > self.last_character:
            raise IndexError("EOF")
        else:
            # We read only one character
            curr_char = self.input_string[self.idx]
            self.idx+=1
            return curr_char
    
    def decrease(self):
        # If we want to set the cursor back
        if self.idx <= 0:
            raise ReferenceError("The index cannot be < 0")
        else:
            self.idx -= 1
    
    def lex(self):
        # We need the next character
        try:
            curr_char = self.advance()
            # Tokenizing
            if curr_char in string.whitespace:
                # Spaces not included
                return self.lex()
            elif curr_char == "{":
                self.token.append(Token(TT_OBJECT_START, curr_char))
            elif curr_char == "}":
                self.token.append(Token(TT_OBJECT_END, curr_char))
            elif curr_char == "'" or curr_char == "\"":
                self.token.append(self.lex_string(q_type=curr_char))
            elif curr_char == ":":
                self.token.append(Token(TT_TUPLE_OPERATOR, curr_char))
            elif curr_char == ",":
                self.token.append(Token(TT_COMMA, curr_char))
            elif curr_char == "[":
                self.token.append(Token(TT_LPAREN, curr_char))
            elif curr_char == "]":
                self.token.append(Token(TT_RPAREN, curr_char))

            elif curr_char.lower() in "0123456789":
                self.decrease()
                self.token.append(self.lex_number())
            else:
                self.decrease()
                # If the curr_char not in all of this acepted sequences
                # we try to parse a true, false, null kw
                self.token.append(self.lex_kw())
            return self.lex()
        except IndexError:
            return self.token
    
    def lex_kw(self, sequence=""):
        
        curr_char = self.advance()
        if curr_char not in " \n,}]:":
            return self.lex_kw(sequence=sequence+curr_char)
        else:
            # We try to parse
            self.decrease()
            if sequence == "true":
                return Token(TT_BOOL, sequence)
            elif sequence == "false":
                return Token(TT_BOOL, sequence)
            elif sequence == "null":
                return Token(TT_NULL, sequence)
            else:
                # If not is a unrecognized token
                raise SyntaxError(f"Unrecognized token {sequence}")

    def lex_string(self, *, q_type, sequence=""):
        curr_char = self.advance()
        if curr_char != q_type:
            # Recursion
            return self.lex_string(q_type=q_type, sequence=sequence+curr_char)
        else:
            # If the character is ' or " we return the string token
            return Token(TT_STRING, sequence)

    def lex_number(self, sequence=""):
        curr_char = self.advance()
        # if not in <whitespace> comma, line-skip or ] } 
        # We just parse the sequence
        if curr_char.lower() in "123456789.":
            if curr_char == ".":
                self.point_count += 1
                if self.point_count > 1:
                    raise SyntaxError(f"The floating point number {sequence+curr_char} have 2 points")
            return self.lex_number(sequence=sequence+curr_char)
        
        elif curr_char in " \n,}]":
            self.decrease()
            self.point_count = 0
            return Token(TT_NUMBER, sequence)


class JSONObject:
    def __init__(self, members) -> None:
        # We store the members as a list
        self.members: list = members
        # We prepare an empty dict to store the result
        self.result = {}        

    def evaluate(self):
        # We evaluate every member 
        # evaluating every member is the way to get the value as string int, object, list etc.
        for member in self.members:
            member.evaluate()
            # We store the value in the corresponding dict key
            self.result[member.key] = member.value
        # We return the result dict
        return self.result
        
    def __str__(self) -> str:
        return str(self.result)
        
class List:
    
    def __init__(self, elements) -> None:
        # The list only store the elements as list objects
        self.elements: list[Token] = elements
        # We create a empty list to store the result
        self.result = []

    def evaluate(self):
        # We convert the tokens to their corresponding datatype
        for value in self.elements:
            if value.type == TT_STRING:
                # We convert the value in string
                self.result.append(str(self.value.value))
            if value.type == TT_BOOL:
                # In bool
                if value.value == "true":
                    self.result.append(True)
                if value.value == "false":
                    self.result.append(False)
            if value.type == TT_NULL:
                # In null or Python's None
                self.result.append(None)
            if value.type == TT_NUMBER:
                # If there is a point in a number type, is interpreted as
                # floating point value
                if "." in value.value:
                    # Float !
                    self.result.append(float(value.value))
                else:
                    # INT !
                    self.result.append(int(value.value))
        return self.result
@dataclass
class Member:
    # The member is the (key, value) tuple of the json values
    key: Token
    value: typing.Union[Token, JSONObject, List]

    def evaluate(self):
        # To evaluate the tuple, the key is assumed to be an string
        if self.key.type != TT_STRING:
            raise SyntaxError("The key must be a string")
        self.key = str(self.key.value)

        # If the value is instance of list or JSON we use the evaluate method for those
        # datatypes
        if isinstance(self.value, List):
            self.value = self.value.evaluate()
            return
        if isinstance(self.value, JSONObject):
            self.value = self.value.evaluate()
            return
        if not isinstance(self.value, Token):
            return

        # We convert the token in their corresponding python's datatype
        if self.value.type == TT_STRING:
            self.value = str(self.value.value)
        elif self.value.type == TT_BOOL:
            if self.value.value == "true":
                self.value = True
            elif self.value.value == "false":
                self.value = False
        elif self.value.type == TT_NULL:
            self.value = None
        elif self.value.type == TT_NUMBER:
            if "." in self.value.value:
                self.value = float(self.value.value)
            else:
                self.value = int(self.value.value)



class Parser:
    # The parser only organize the Tokens in a logic manner
    def __init__(self, tokenizer) -> None:
        self.tokens = tokenizer.lex()
        self.idx = 0
        self.ast = []
    
    def next_token(self):
        if len(self.tokens) > 0:
            self.idx += 1
            return self.tokens[self.idx]
        else:
            return False
    
    def decrease(self):
        self.idx -= 1

    def parse(self):
        try:
            # Here is where the magic begin
            curr_token = self.next_token()
            # If the current token is [ we pase the list
            if curr_token.type == TT_LPAREN:
                self.ast.append(self.parse_list())
            # If the current token is : we parse the member
            elif curr_token.type == TT_TUPLE_OPERATOR:
                self.ast.append(self.parse_member())
            # If the current token is { we parse the object
            elif curr_token.type == TT_OBJECT_START:
                self.ast.append(self.parse_object())
            return self.parse()
        
        except IndexError:
            # Well and if aren't more tokens, we return the evaluated result
            # as dict
            return JSONObject(self.ast).evaluate()

    def parse_list(self, elements=[]):
        try:
            # To parse a list, we parse all the members untill we have a RPAREN (])
            curr_token = self.next_token()
            if curr_token.value != ",":
                elements.append(curr_token)
            if curr_token.type == TT_LPAREN:
                elements.append(self.parse_list())
            elif curr_token.type == TT_TUPLE_OPERATOR:
                elements.append(self.parse_member())
            elif curr_token.type == TT_OBJECT_START:
                elements.append(self.parse_object())
            elif curr_token.type == TT_RPAREN:
                return List(elements)
            
            return self.parse_list(elements=elements)

        except IndexError:
            raise "The list was not closed"

    def parse_object(self, elements=[]):

        try:
            # To parse an object is the same method as parse, but is 
            # for an inner json object
            curr_token = self.next_token()

            if curr_token.type == TT_LPAREN:
                elements.append(self.parse_list())
            elif curr_token.type == TT_TUPLE_OPERATOR:
                elements.append(self.parse_member())
            elif curr_token.type == TT_OBJECT_START:
                elements.append(self.parse_object())
            elif curr_token.type == TT_OBJECT_END:
                return JSONObject(elements).evaluate()
            
            return self.parse_object(elements)

        except IndexError:
            raise "The object was not closed"
        
    def parse_member(self):
        # To parse a member we localize the key and the value
        self.decrease()
        self.decrease()

        key = self.next_token()
        self.next_token()
        value = self.next_token()

        # If this value is [ we parse a list
        if value.type == TT_LPAREN:
            value = self.parse_list()
        # If this value is { we parse an object
        elif value.type == TT_OBJECT_START:
            value = self.parse_object()
        # We return the member
        return Member(key, value)


if __name__ == "__main__":
    i_string = "{'key':'value', 'key2': 42.2, 'error': true, 'obj': {'hello': 'adios'}, 'lista': [1,2,3]}"
    lex = Lexer(i_string)
    parser = Parser(lex).parse()
    pprint(parser)
