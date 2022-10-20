import unittest
import main

class TextMain(unittest.TestCase):
    def test_lex_init(self):
        i_string = "{'key': 'value'}"
        lex = main.Lexer(i_string)
        self.assertEqual(lex.input_string, i_string)
        self.assertEqual(lex.idx, 0)
        self.assertEqual(lex.last_character, len(i_string)-1)
    
    def test_lex_advande_exceptions(self):
        i_string = r"{}"
        lex = main.Lexer(i_string)

        with self.assertRaises(IndexError):
            lex.advance()
            lex.advance()
            lex.advance()
        
        i_string = r"{}"
        lex = main.Lexer(i_string)
        
        with self.assertRaises(ReferenceError):
            lex.decrase()

    def test_lex_advance_and_decrease(self):
        i_string = "{'key': 'value'}"
        lex = main.Lexer(i_string)
        self.assertEqual(lex.advance(), "{")
        
        lex.decrase()
        self.assertEqual(lex.advance(), "{")
    
    def test_lex_parsing_simple_object(self):
        i_string = "{'key':'value'}"
        lex = main.Lexer(i_string)
        result = lex.lex()
        
        expected = [
            main.Token(main.TT_OBJECT_START, "{"), 
            main.Token(main.TT_STRING, "key"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_STRING, "value"),
            main.Token(main.TT_OBJECT_END, "}")
            ]
        
        self.assertEqual(result, expected)

    def test_lex_parsing_a_little_more_complex_object(self):
        i_string = "{'key':'value', 'key2': 42, 'error': true, 'null':null, 'list':[42, 45]}"
        lex = main.Lexer(i_string)
        result = lex.lex()
        
        expected = [
            main.Token(main.TT_OBJECT_START, "{"), 
            main.Token(main.TT_STRING, "key"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_STRING, "value"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "key2"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_NUMBER, "42"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "error"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_BOOL, "true"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "null"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_NULL, "null"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "list"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_LPAREN, "["),
            main.Token(main.TT_NUMBER, "42"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_NUMBER, "45"),
            main.Token(main.TT_RPAREN, "]"),
            main.Token(main.TT_OBJECT_END, "}")]
        
        self.assertEqual(result, expected)

    def test_lex_parsing_a_little_little_more_complex_object(self):
        i_string = "{'key':'value', 'key2': 42.2, 'error': true}"
        lex = main.Lexer(i_string)
        result = lex.lex()
        
        expected = [
            main.Token(main.TT_OBJECT_START, "{"), 
            main.Token(main.TT_STRING, "key"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_STRING, "value"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "key2"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_NUMBER, "42.2"),
            main.Token(main.TT_COMMA, ","),
            main.Token(main.TT_STRING, "error"),
            main.Token(main.TT_TUPLE_OPERATOR, ":"),
            main.Token(main.TT_BOOL, "true"),
            main.Token(main.TT_OBJECT_END, "}")]
        self.assertEqual(result, expected)
    
    def test_lex_raises_float_error(self):
        i_string = "{'key':'value', 'key2': 42.2.1, 'error': true}"
        lex = main.Lexer(i_string)
        with self.assertRaises(SyntaxError):
            result = lex.lex()
        