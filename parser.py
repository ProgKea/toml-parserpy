import sys

Tokens = [
    "TOKEN_LEFT_BRACKET",
    "TOKEN_RIGHT_BRACKET",
    "TOKEN_LEFT_BRACE",
    "TOKEN_RIGHT_BRACE",
    "TOKEN_IDENTIFIER",
    "TOKEN_NEW_LINE",
    "TOKEN_EQUAL",
    "TOKEN_STRING",
    "TOKEN_COMMENT",
    "TOKEN_COMMA",
    "TOKEN_NUMBER",
]
Token_Kind = {t: i for i, t in enumerate(Tokens)}

def read_entire_file(file_path):
    with open(file_path) as f:
        return f.read()

class Token():
    def __init__(self, kind, text):
        self.kind = kind
        self.text = text

    def print(self):
        print(repr(self.text), Tokens[self.kind])

class Lexer():
    def __init__(self, content):
        self.content = content
        self.cursor = 0

    def get_current_char(self):
        if self.cursor >= len(self.content): return
        return self.content[self.cursor]

    def chop(self):
        if self.cursor >= len(self.content): return
        self.cursor += 1

    def chop_to(self, chars) -> str:
        x = self.get_current_char()
        chopped = ""
        while True:
            x = self.get_current_char()
            if x == None: break
            elif x in chars: break
            chopped += x
            self.chop()
        return chopped

    def next(self) -> Token:
        if self.cursor >= len(self.content): return None
        x = self.get_current_char()
        self.chop()
        match x:
            case '[':
                return Token(Token_Kind["TOKEN_LEFT_BRACKET"], x)
            case ']':
                return Token(Token_Kind["TOKEN_RIGHT_BRACKET"], x)
            case '{':
                return Token(Token_Kind["TOKEN_LEFT_BRACE"], x)
            case '}':
                return Token(Token_Kind["TOKEN_RIGHT_BRACE"], x)
            case '\n':
                return Token(Token_Kind["TOKEN_NEW_LINE"], x)
            case ' ':
                return self.next()
            case '=':
                return Token(Token_Kind["TOKEN_EQUAL"], x)
            case ',':
                return Token(Token_Kind["TOKEN_COMMA"], x)
            case '"':
                text = self.chop_to('"') + self.get_current_char()
                self.cursor += 1
                return Token(Token_Kind["TOKEN_STRING"], x + text)
            case '#':
                return Token(Token_Kind["TOKEN_COMMENT"], x + self.chop_to("\n"))
            case other:
                token_kind = None
                if x.isdigit(): token_kind = Token_Kind["TOKEN_NUMBER"]
                else: token_kind = Token_Kind["TOKEN_IDENTIFIER"]
                return Token(token_kind, x + self.chop_to(",\n#\"= ]"))

class Parser():
    def __init__(self, content):
        self.content = content
        self.lexer = Lexer(self.content)
        self.current_head = ""
        self.ast = {}

    def wrong_token(self, expected_i, got_i):
        expected = Tokens[expected_i]
        got = Tokens[got_i]
        sys.stderr.write(f"ERROR: Expected {expected}, got {got}\n")
        exit(1)

    def expect_next(self, expected_i):
        got_i = self.lexer.next().kind
        if got_i != expected_i:
            self.wrong_token(expected_i, got_i)

    def unexpected_token(self, token):
        sys.stderr.write(f"ERROR: Unexpected Token {repr(token.text)}\n")
        exit(1)

    def convert_ident(self, token):
        if token.kind == Token_Kind["TOKEN_NUMBER"]:
            return float(token.text)
        elif token.kind == Token_Kind["TOKEN_STRING"]:
            return token.text[1:-1]
        else:
            self.unexpected_token(token)

    def parse(self):
        while True:
            token = self.lexer.next()
            if token == None: return self.ast
            kind = token.kind
            if kind == Token_Kind["TOKEN_LEFT_BRACKET"]:
                self.current_head = self.lexer.next()
                self.expect_next(Token_Kind["TOKEN_RIGHT_BRACKET"])
                self.ast[self.current_head.text] = {}
            elif kind == Token_Kind["TOKEN_RIGHT_BRACKET"]:
                self.unexpected_token(token)
            elif kind == Token_Kind["TOKEN_IDENTIFIER"]:
                self.ast[self.current_head.text][token.text] = None
                self.last_var = token
            elif kind == Token_Kind["TOKEN_EQUAL"]:
                next_token = self.lexer.next()
                if next_token.kind == Token_Kind["TOKEN_LEFT_BRACKET"]:
                    value = []
                    while True:
                        t = self.lexer.next()
                        if t == None or t.kind == Token_Kind["TOKEN_RIGHT_BRACKET"]: break
                        if t.kind == Token_Kind["TOKEN_COMMA"]: continue
                        value.append(self.convert_ident(t))
                else:
                    value = self.convert_ident(next_token)
                self.ast[self.current_head.text][self.last_var.text] = value
            elif kind == Token_Kind["TOKEN_COMMENT"] or kind == Token_Kind["TOKEN_NEW_LINE"]:
                pass
            else:
                return self.ast

parser = Parser(read_entire_file("test.toml"))
ast = parser.parse()
print(repr(ast))

# TODO: Show where a syntax error has happened
