DEBUG = True




class Token:
    def __init__(self, token_type, lexeme, line_number=1):
        self.type = token_type
        self.lexeme = lexeme
        self.line_number = line_number
   
    def __str__(self):
        return f"Token: {self.type:<15} Lexeme: {self.lexeme}"


def lexer(source):
    tokens = []
    i = 0
    length = len(source)
    line_number = 1
   
    keywords = ["if", "else", "endif", "while", "endwhile", "for",
               "function", "return", "integer", "boolean",
               "print", "scan", "true", "false"]
    operators = ["==", "!=", "<=", "=>", "+", "-", "*", "/", "=", "<", ">"]
    separators = [",", ";", "(", ")", "{", "}", "$$"]
   
    while i < length:
        # Track line numbers for better error reporting
        if source[i] == '\n':
            line_number += 1
            i += 1
            continue
           
        if source[i].isspace():
            i += 1
            continue




        # Look for comments - we don't tokenize these, just skip over them
        if i + 1 < length and source[i:i+2] == "/*":
            comment_start_line = line_number  # Track starting line for error reporting
            i += 2
            while i + 1 < length and source[i:i+2] != "*/":
                if source[i] == '\n':
                    line_number += 1
                i += 1
           
            if i + 1 < length:
                i += 2  # Skip over the */
            else:
                # Report unclosed comment but don't add to tokens
                print(f"Warning: Unclosed comment starting at line {comment_start_line}")
            continue
           
        # Check for [* *] style comments - skip over these too
        if i + 1 < length and source[i:i+2] == "[*":
            comment_start_line = line_number
            i += 2
            while i + 1 < length and source[i:i+2] != "*]":
                if source[i] == '\n':
                    line_number += 1
                i += 1
           
            if i + 1 < length:
                i += 2  # Skip over the *]
            else:
                # Report unclosed comment but don't add to tokens
                print(f"Warning: Unclosed comment starting at line {comment_start_line}")
            continue




        # Look for $$
        if i + 1 < length and source[i:i+2] == "$$":
            tokens.append(Token("separator", "$$", line_number))
            i += 2  # Go past $$
            continue








        # Handle identifiers (keywords and variable names)
        if source[i].isalpha():
            isError = False
            start = i
            i += 1  # Move past the first character that we already checked
            while (i < length and
                   source[i] not in [" ", "\n", "(", ")", "{", "}", ";", ","] and
                   not (i + 1 < length and source[i:i+2] == "$$")):
                i += 1
            lexeme = source[start:i]
           
            # First check if it's a keyword (before checking for valid identifier characters)
            if lexeme.lower() in keywords:  # Case-insensitive keywords
                tokens.append(Token("keyword", lexeme.lower(), line_number))
            # Then check if it's a valid identifier
            elif all(c.isalnum() or c == "_" for c in lexeme):
                tokens.append(Token("identifier", lexeme, line_number))
            # Otherwise, it's an error
            else:
                tokens.append(Token("error", lexeme, line_number))
            continue








        # Handle invalid reals beginning with .
        if source[i] == '.':
            start = i
            i += 1
            while (i < length and
                   source[i] not in [" ", "\n", "(", ")", "{", "}", ";", ","] and
                   not (i + 1 < length and source[i:i+2] == "$$")):
                i += 1
            lexeme = source[start:i]
            tokens.append(Token("error", lexeme, line_number))
            continue




        # Handle numbers (integers and real numbers)
        if source[i].isdigit():
            isError = False
            start = i
            i += 1  # Move past the first digit that we already checked
            while (i < length and
                   source[i] not in [" ", "\n", "(", ")", "{", "}", ";", ","] and
                   not (i + 1 < length and source[i:i+2] == "$$")):
                if not source[i].isdigit() and source[i] != '.':
                    isError = True    
                i += 1
            lexeme = source[start:i]
            if lexeme.count(".") > 1:
                tokens.append(Token("error", lexeme, line_number))
            elif '.' in lexeme and lexeme.count(".") == 1:
                sides = lexeme.split('.')
                if sides[0].isdigit() and sides[1].isdigit():
                    tokens.append(Token("error", lexeme, line_number))
                else:
                    tokens.append(Token("error", lexeme, line_number))
            else:
                if isError:
                    tokens.append(Token("error", lexeme, line_number))
                else:
                    tokens.append(Token("integer", lexeme, line_number))
            continue
       
        # Handle single-character separators
        if source[i] in separators and not (i + 1 < length and source[i:i+2] == "$$"):  
            tokens.append(Token("separator", source[i], line_number))
            i += 1
            continue




        # Handle operators (check multi-character first)
        if i + 1 < length and source[i:i+2] in operators:
            tokens.append(Token("operator", source[i:i+2], line_number))
            i += 2
            continue
        if source[i] in operators:
            tokens.append(Token("operator", source[i], line_number))
            i += 1
            continue




       
        # If no known token type is found, mark it as an invalid token
        # and report it, but still include it for error reporting
        else:
            start = i
            i += 1  # Move past the first character
            while (i < length and
                   source[i] not in [" ", "\n", "(", ")", "{", "}", ";", ","] and
                   not (i + 1 < length and source[i:i+2] == "$$")):
                i += 1
            lexeme = source[start:i]
            print(f"Invalid token '{lexeme}' at line {line_number}")
            tokens.append(Token("invalid", lexeme, line_number))
   
    return tokens




class Parser:
    def __init__(self, tokens, print_productions=True):
        self.tokens = tokens
        self.index = 0
        self.print_productions = print_productions
        self.output_lines = []
        self.error_count = 0
        self.global_vars = {}  
        self.scope_stack = []  # Contain dictionaries
        self.functions = {}  # Store function names and parameters
        self.current_line = 1 if tokens else 0
        self.in_loop_body = False  # Track if we're parsing a loop body
        self.in_if_body = False    # Track if we're parsing an if body
        self.last_matched_token = None
        self.current_var_type = None  # Track the current variable type during declarations
        self.memAddrList = []
        self.assemblyList = []




    def currentToken(self):
        if self.index < len(self.tokens):
            token = self.tokens[self.index]
            self.current_line = token.line_number
            return token
        return Token("EOF", "", self.current_line)




    def lookAhead(self, steps=1):
        """Look ahead n tokens without consuming them"""
        if self.index + steps < len(self.tokens):
            return self.tokens[self.index + steps]
        return Token("EOF", "", self.current_line)




    def nextToken(self):
        token = self.currentToken()
        self.last_matched_token = token
        # Print token and lexeme in the required format
        self.output_token(token)
        self.index += 1
        return self.currentToken()
   
    def output_token(self, token):
        if token.type != "EOF":
            self.output_lines.append(f"Token: {token.type:<15} Lexeme: {token.lexeme}")




    def match(self, expected_type, expected_lexeme=None):
        token = self.currentToken()
        if token.type == expected_type and (expected_lexeme is None or token.lexeme == expected_lexeme):
            next_token = self.nextToken()
            return True
        else:
            expected_desc = f"{expected_type}{' ' + expected_lexeme if expected_lexeme else ''}"
            found_desc = f"{token.type}{' ' + token.lexeme if token.lexeme else ''}"
            self.error(f"Expected {expected_desc} but found {found_desc}")
            return False




    def error(self, message):
        error_msg = f"Syntax error at line {self.current_line}: {message}"
        self.output_lines.append(error_msg)
        self.error_count += 1
       
        # Enhanced error recovery with more context-aware decisions
        token = self.currentToken()
       
       
           
        # Special case for endif/endwhile - don't skip these important structure markers
        if token.type == "keyword" and token.lexeme in ["endif", "endwhile", "else"]:
            return
               
        # More robust error recovery - skip to a synchronizing token
        recovery_attempted = False
        while self.index < len(self.tokens):
            token = self.currentToken()
           
            # Stop at semicolons - a common statement boundary
            if (token.type == "separator" and token.lexeme == ";"):
                self.nextToken()  # Consume the semicolon
                recovery_attempted = True
                break
               
            # Stop at keywords that often start statements
            elif (token.type == "keyword" and
                    token.lexeme in ["if", "while", "function", "return", "endif", "endwhile", "else"]):
                recovery_attempted = True
                break
               
            # Stop at section separators
            elif token.type == "separator" and token.lexeme == "$$":
                recovery_attempted = True
                break
               
            # Stop at closing braces - end of block
            elif token.type == "separator" and token.lexeme == "}":
                recovery_attempted = True
                break
               
            else:
                self.index += 1  # Skip the current token
       
        # If we couldn't find a synchronizing token, advance just one token to avoid infinite loops
        if not recovery_attempted and self.index < len(self.tokens):
            self.index += 1




    def printProduction(self, production):
        if self.print_productions:
            self.output_lines.append(production)


    # Scope Management - can track types
    def enterScope(self):
        """Create a new scope."""
        self.scope_stack.append({})  # Dictionary




    def exitScope(self):
        """Exit the current scope."""
        if self.scope_stack:
            self.scope_stack.pop()




    def declareVariable(self, var_name, var_type):
        """Declare a variable with its type in the current scope or globally."""
        if self.scope_stack:
            # Check if variable exists in the current scope (not the entire stack)
            if var_name not in self.scope_stack[-1]:
                self.scope_stack[-1][var_name] = var_type
            else:
                self.error(f"{var_name} already declared. Declaration unnecessary.")
        else:
            if var_name not in self.global_vars:
                if len(self.global_vars) == 0:
                    memAddr = 10000
                else:
                    memAddr = self.memAddrList[-1] + 1
                self.global_vars[var_name] = var_type
                self.memAddrList.append(memAddr)
            else:
                self.error(f"{var_name} already declared. Declaration unnecessary.")




    def isVariableDeclared(self, var_name):
        """Check if a variable is declared in any accessible scope."""
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                return True
        return var_name in self.global_vars




    def getVariableType(self, var_name):
        """Get the type of a declared variable."""
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                return scope[var_name]
        if var_name in self.global_vars:
            return self.global_vars[var_name]
        return None




    # Type checking helpers
    def areTypesCompatible(self, target_type, expr_type):
        """Check if an expression type is compatible with a target variable type."""
        if target_type == expr_type:
            return True
    
        # Special case for boolean and integer 0/1
        if target_type == "boolean" and expr_type == "integer":
            # Look at the current token directly
            curr_idx = self.index - 1  # Start from one position back
        
            # Find the relevant integer token that would be part of this assignment
            integer_token = None
            for i in range(curr_idx, max(0, curr_idx - 5), -1):
                if i < len(self.tokens) and self.tokens[i].type == "integer" and self.tokens[i].lexeme in ["0", "1"]:
                    integer_token = self.tokens[i]
                    break
            
            if integer_token and integer_token.lexeme in ["0", "1"]:
                # Look for operators that would make this part of an expression
                has_operators = False
                for i in range(curr_idx, max(0, curr_idx - 5), -1):
                    if i < len(self.tokens) and self.tokens[i].type == "operator" and self.tokens[i].lexeme in ["+", "-", "*", "/"]:
                        has_operators = True
                        break
                
                # If it's a simple 0 or 1 without operators, allow the conversion
                if not has_operators:
                    return True
        
        # No automatic type conversions allowed between booleans and numeric types
        if target_type == "boolean" or expr_type == "boolean":
            return False
        
        return False




    def determineExpressionType(self):
        """Determine the type of an expression at the current position."""
        token = self.currentToken()
   
        # Handle simple literals
        if token.type == "integer":
            return "integer"
        elif token.type == "keyword" and token.lexeme in ["true", "false"]:
            return "boolean"
        elif token.type == "identifier":
            # Check if it's a function call
            next_token = self.lookAhead()
            if next_token.type == "separator" and next_token.lexeme == "(":
                # It's a function call, get its return type
                if token.lexeme in self.functions and isinstance(self.functions[token.lexeme], dict):
                    return self.functions[token.lexeme].get("return_type", "unknown")
                return "unknown"
            # Otherwise it's a variable
            return self.getVariableType(token.lexeme)
           
        # For parenthesized expressions
        if token.type == "separator" and token.lexeme == "(":
            # Save position
            saved_index = self.index
               
            # Skip the opening parenthesis
            self.index += 1
               
            # Try to determine the type of the expression inside
            expr_type = self.determineExpressionType()
               
            # Restore position
            self.index = saved_index
               
            return expr_type
           
        # Check for operations (addition, subtraction, multiplication, division)
        # Look ahead for operators
        next_idx = self.index + 1
        while next_idx < len(self.tokens):
            next_token = self.tokens[next_idx]
            # If we find an operator, the expression will be of integer type
            if next_token.type == "operator" and next_token.lexeme in ["+", "-", "*", "/"]:
                return "integer"
            next_idx += 1
       
        return "unknown"






    # Parsing Functions with the Production Rules
    def parseProgram(self):
        self.printProduction("<Program> -> <Statement List>")
        self.parseStatementList()




    def parseStatementList(self):
        self.printProduction("<Statement List> -> <Statement> <Statement List> | ε")
       
        while self.index < len(self.tokens) and self.currentToken().type != "EOF":
            token = self.currentToken()
           
            # Handle section separator
            if token.type == "separator" and token.lexeme == "$$":
                self.match("separator", "$$")
                continue
               
            # Check for end of block markers - these are handled by their parent statements
            if (token.type == "keyword" and
                token.lexeme in ["endif", "endwhile", "else"]):
                break
               
            # Try to parse a statement, but allow for error recovery
            try:
                self.parseStatement()
            except Exception as e:
                print(f"Error during parsing: {e}")
                # Attempt recovery to continue parsing
                self.error(f"Exception: {str(e)}")
                # Ensure we advance at least one token to avoid infinite loops
                if self.index < len(self.tokens):
                    self.index += 1




    def parseStatement(self):
        self.printProduction("<Statement> -> <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While> | <Declaration>")
       
        token = self.currentToken()
       
        if token.type == "keyword" and token.lexeme == "function":
            self.parseFunctionDef()
        elif token.type == "keyword" and token.lexeme == "if":
            self.parseIfStmt()
        elif token.type == "keyword" and token.lexeme == "while":
            self.parseWhileStmt()
        elif token.type == "keyword" and token.lexeme == "return":
            self.parseReturnStmt()
        elif token.type == "keyword" and token.lexeme in ["integer", "boolean"]:
            self.parseVarDec()
        elif token.type == "keyword" and token.lexeme == "print":
            self.parsePrintStmt()
        elif token.type == "keyword" and token.lexeme == "scan":
            self.parseScanStmt()
        elif token.type == "identifier":
            # Look ahead to see if it's an assignment or function call
            if self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].type == "operator" and self.tokens[self.index + 1].lexeme == "=":
                self.parseAssignment()
            else:
                self.parseFunctionCall()
        elif token.type == "separator" and token.lexeme == "{":
            self.parseCompound()
        else:
            # Special handling for keywords not recognized at statement level
            if token.type == "keyword":
                if token.lexeme in ["endif", "endwhile", "else"]:
                    # These are handled by their respective statement parsers
                    return
                elif token.lexeme in ["true", "false"]:
                    # Boolean literals aren't statements on their own
                    self.error(f"Boolean literal '{token.lexeme}' cannot be used as a statement")
                    self.nextToken()
                    return
                   
            self.error(f"Unexpected token in statement: {token.lexeme}")
            # Move past the problematic token
            self.nextToken()




    def parseCompound(self):
        self.printProduction("<Compound> -> { <Statement List> }")
        self.enterScope()
       
        if not self.match("separator", "{"):
            self.exitScope()
            return
           
        # Parse statements until we encounter a closing brace or EOF
        while (self.index < len(self.tokens) and
               (self.currentToken().type != "separator" or self.currentToken().lexeme != "}")):
            if self.currentToken().type == "EOF":
                self.error("Unexpected end of file in compound statement")
                self.exitScope()
                return
           
            # Check for end of block markers inside compound statement
            token = self.currentToken()
            if (token.type == "keyword" and
                token.lexeme in ["endif", "endwhile"]):
                break
               
            self.parseStatement()
       
        self.match("separator", "}")
        self.exitScope()
       
    def parseFunctionDef(self):
        self.printProduction("<Function> -> function <Identifier> ( <Parameter List> ) <Compound>")


        if not self.match("keyword", "function"):
            return
   
        function_name = self.currentToken().lexeme
        if function_name in self.functions:
            self.error(f"Function {function_name} already defined")


        if not self.match("identifier"):
            return
   
        if not self.match("separator", "("):
            return


        self.enterScope()
        params = self.parseParameterList()  # Modified to return parameter info
   
        # Add a placeholder for return type - it'll be determined by return statements
        self.functions[function_name] = {"params": params, "return_type": "unknown"}  # Changed to unknown
   
        if not self.match("separator", ")"):
            self.exitScope()
            return
           
        self.parseCompound()
        self.exitScope()
       
    def parseScanStmt(self):
        self.printProduction("<Scan> -> scan ( <IDs> );")
   
        if not self.match("keyword", "scan"):
            return
       
        if not self.match("separator", "("):
            return
       
        # Collect variables being scanned to later add their POPM instructions
        scanned_vars = []
        self.parseIDsScan(scanned_vars)
   
        if not self.match("separator", ")"):
            return
       
        self.match("separator", ";")


        # Append SIN instruction
        self.assemblyList.append("SIN")
       
        # POPM instructions for each variable in reversed order
        for var_name in reversed(scanned_vars):
            # Get memory address for the variable
            mem_addr = None
            for i, var in enumerate(self.global_vars.keys()):
                if var == var_name:
                    mem_addr = self.memAddrList[i]
                    break
           
            # Add POPM instruction to store the input value into variable's memory location
            if mem_addr is not None:
                self.assemblyList.append(f"POPM      {mem_addr}")


    def parseIDsScan(self, scanned_vars=None):
        """Parse IDs for scan statement with validation for declared variables"""
        self.printProduction("<IDs> -> <Identifier> <IDsPrime>")
   
        var_name = self.currentToken().lexeme
   
        # Check if variable is declared before scanning
        if not self.isVariableDeclared(var_name):
            self.error(f"Variable '{var_name}' used in scan procedure without prior declaration.")
   
        # Add variable to the list of scanned variables
        if scanned_vars is not None:
            scanned_vars.append(var_name)
   
        if not self.match("identifier"):
            return
   
        self.parseIDsPrimeScan(scanned_vars)


    def parseIDsPrimeScan(self, scanned_vars=None):
        self.printProduction("<IDsPrime> -> , <Identifier> <IDsPrime> | ε")
   
        if self.currentToken().type == "separator" and self.currentToken().lexeme == ",":
            self.match("separator", ",")
            var_name = self.currentToken().lexeme
       
            if not self.isVariableDeclared(var_name):
                self.error(f"Variable '{var_name}' used in scan procedure without prior declaration.")
       
            # Add variable to the list of scanned variables
            if scanned_vars is not None:
                scanned_vars.append(var_name)
       
            if not self.match("identifier"):
                return
           
            self.parseIDsPrimeScan(scanned_vars)
        else:
            self.printProduction("<IDsPrime> -> ε")




    def parsePrintStmt(self):
        self.printProduction("<Print> -> print ( <Expression> );")
   
        if not self.match("keyword", "print"):
            return
       
        if not self.match("separator", "("):
            return
   
        # Parse expression normally without skipping PUSHM instructions
        self.parseExpression()
   
        # Append a SOUT instruction after expression is parsed
        self.assemblyList.append("SOUT")
   
        if not self.match("separator", ")"):
            return
       
        self.match("separator", ";")






    def parseParameterList(self):
        self.printProduction("<Parameter List> -> <Parameter> <Parameter List Prime> | ε")
   
        params = []
   
        # Check if we're at a parameter
        if self.currentToken().type == "identifier":
            param = self.parseParameter()  # return name and type
            if param:
                params.append(param)
            params.extend(self.parseParameterListPrime())  # return parameters
        else:
            self.printProduction("<Parameter List> -> ε")
       
        return params




    def parseParameterListPrime(self):
        self.printProduction("<Parameter List Prime> -> , <Parameter> <Parameter List Prime> | ε")
   
        params = []
   
        if self.currentToken().type == "separator" and self.currentToken().lexeme == ",":
            self.match("separator", ",")
            param = self.parseParameter()
            if param:
                params.append(param)
            params.extend(self.parseParameterListPrime())
        else:
            self.printProduction("<Parameter List Prime> -> ε")
       
        return params




    def parseParameter(self):
        self.printProduction("<Parameter> -> <IDs> <Qualifier>")
   
        var_name = self.currentToken().lexeme
        if not self.match("identifier"):
            return None
   
        # Store the variable name temporarily
        temp_var_name = var_name
   
        # Get the type from qualifier
        token = self.currentToken()
        var_type = token.lexeme if token.type == "keyword" and token.lexeme in ["integer", "boolean"] else "unknown"
   
        self.parseQualifier()
   
        # Now declare the variable with its type
        self.declareVariable(temp_var_name, var_type)
   
        return (temp_var_name, var_type)




    def parseQualifier(self):
        self.printProduction("<Qualifier> -> integer | boolean")
       
        token = self.currentToken()
        if token.type == "keyword" and token.lexeme in ["integer", "boolean"]:
            # Store the current variable type
            self.current_var_type = token.lexeme
            self.match("keyword", token.lexeme)
        else:
            self.error("Type qualifier expected (integer or boolean)")




    def parseIfStmt(self):
        self.printProduction("<If> -> if ( <Condition> ) <Statement> <IfPrime>")
   
        # Scope for the entire if/else structure
        self.enterScope()
        previous_if_body = self.in_if_body
        self.in_if_body = True
   
        if not self.match("keyword", "if"):
            self.in_if_body = previous_if_body
            self.exitScope()
            return
           
        if not self.match("separator", "("):
            self.in_if_body = previous_if_body
            self.exitScope()
            return
       
        # Save pos to add the JMP0 instruction at a future time
        condition_position = len(self.assemblyList)
       
        self.parseCondition()
       
        if not self.match("separator", ")"):
            self.in_if_body = previous_if_body
            self.exitScope()
            return
       
        # Add JMP0 instruction with a placeholder for the label
        self.assemblyList.append("JMP0      TBD")
        jmp_position = len(self.assemblyList) - 1
       
        # Create a separate scope for the if body regardless of curly braces
        self.enterScope()
        self.parseStatement()
        # Exit the if body scope before entering else
        self.exitScope()
       
        # If there's an else coming, add a jump to skip it after the 'if' body completes
        next_token = self.currentToken()
        if next_token.type == "keyword" and next_token.lexeme == "else":
            self.assemblyList.append("JMP0       TBD")
            else_jmp_position = len(self.assemblyList) - 1
           
            # Add label for the else part. This is where JMP0 should jump to if condition is false
            self.assemblyList.append("LABEL")
            else_label_position = len(self.assemblyList) - 1
           
            # Update the JMP0 instruction with the correct label position
            self.assemblyList[jmp_position] = f"JMP0      {else_label_position + 1}"
        else:
            # Add label where to jump if condition is false
            self.assemblyList.append("LABEL")
            end_if_label_position = len(self.assemblyList) - 1
           
            # Update the JMP0 instruction with the correct label position
            self.assemblyList[jmp_position] = f"JMP0      {end_if_label_position + 1}"
       
        self.parseIfPrime()
       
        # If we had an else branch, resolve its jump position here
        if next_token.type == "keyword" and next_token.lexeme == "else":
            # Add label for the end of the if/else structure
            self.assemblyList.append("LABEL")
            end_label_position = len(self.assemblyList) - 1
           
            # Update the JMP instruction that skips the else block
            self.assemblyList[else_jmp_position] = f"JMP       {end_label_position + 1}"
       
        self.in_if_body = previous_if_body
        # Exit the overall if-else construct scope
        self.exitScope()




    def parseIfPrime(self):
        self.printProduction("<IfPrime> -> else <Statement> endif | endif")
       
        token = self.currentToken()
        if token.type == "keyword" and token.lexeme == "else":
            self.match("keyword", "else")
            # Create a separate scope for the else statement
            self.enterScope()
            self.parseStatement()
            self.exitScope()
            if not self.match("keyword", "endif"):
                self.error("Expected 'endif' after else clause")
        elif token.type == "keyword" and token.lexeme == "endif":
            self.match("keyword", "endif")
        else:
            self.error("Expected 'else' or 'endif'")




    def parseWhileStmt(self):
        self.printProduction("<While> -> while ( <Condition> ) <Statement List> endwhile")
   
        self.enterScope()
        previous_loop_body = self.in_loop_body
        self.in_loop_body = True
   
        if not self.match("keyword", "while"):
            self.in_loop_body = previous_loop_body
            self.exitScope()
            return
       
        if not self.match("separator", "("):
            self.in_loop_body = previous_loop_body
            self.exitScope()
            return
       
        # Add LABEL at the beginning of while loop
        self.assemblyList.append("LABEL")
        start_label_position = len(self.assemblyList) - 1
           
        self.parseCondition()
       
        if not self.match("separator", ")"):
            self.in_loop_body = previous_loop_body
            self.exitScope()
            return
       
        # Add JMP0 instruction with a placeholder to be updated after we know where the loop ends
        self.assemblyList.append("JMP0      TBD")
        jmp0_position = len(self.assemblyList) - 1
       
        # Check if the next token is an opening brace
        if self.currentToken().type == "separator" and self.currentToken().lexeme == "{":
            self.parseCompound()
        else:
            prev_index = self.index  # Save the current position
           
            # Parse the statement
            self.parseStatement()
           
            # Check if endwhile immediately follows
            if self.currentToken().type == "keyword" and self.currentToken().lexeme == "endwhile":
                pass
            else:
                # If we didn't immediately hit endwhile, continue parsing statements
                while (self.index < len(self.tokens) and
                      not (self.currentToken().type == "keyword" and
                            self.currentToken().lexeme == "endwhile")):
                    if self.currentToken().type == "EOF":
                        self.error("Unexpected end of file in while loop")
                        self.in_loop_body = previous_loop_body
                        self.exitScope()
                        return
                       
                    # Check for separators that should end the loop
                    if self.currentToken().type == "separator" and self.currentToken().lexeme == "$$":
                        self.error("Expected 'endwhile' before end of section")
                        break
                       
                    # Continue parsing statements in the loop body
                    self.parseStatement()
       
        # Add unconditional JMP back to the condition evaluation
        self.assemblyList.append(f"JMP       {start_label_position + 1}")
       
        # Add LABEL for the end of the loop where we jump to if condition is false
        self.assemblyList.append("LABEL")
        end_label_position = len(self.assemblyList) - 1
       
        # Update the JMP0 instruction with the correct label position
        self.assemblyList[jmp0_position] = f"JMP0      {end_label_position + 1}"
       
        # matching of the endwhile keyword
        if self.currentToken().type == "keyword" and self.currentToken().lexeme == "endwhile":
            self.match("keyword", "endwhile")
        else:
            self.error("Expected 'endwhile' to close while loop")
           
        self.in_loop_body = previous_loop_body
        self.exitScope()




    def parseCondition(self):
        self.printProduction("<Condition> -> <Expression> <Relop> <Expression>")
       
        # Save position before parsing first expression
        expr1_start_index = self.index
       
        self.parseExpression()
       
        # Save the operator token
        relop_token = self.currentToken()
        relop_operator = relop_token.lexeme
        self.parseRelop()
       
        # Save position before parsing second expression
        expr2_start_index = self.index
       
        self.parseExpression()
       
        # Add comparison instruction based on type of relational operator
        if relop_operator == "==":
            self.assemblyList.append("EQU")
        elif relop_operator == "!=":
            self.assemblyList.append("NEQ")
        elif relop_operator == ">":
            self.assemblyList.append("GRT")
        elif relop_operator == "<":
            self.assemblyList.append("LES")
        elif relop_operator == "<=":
            self.assemblyList.append("LEQ")
        elif relop_operator == "=>":
            self.assemblyList.append("GEQ")
       
        # Reset to determine expression types
        saved_index = self.index
       
        # Determine type of first expression
        self.index = expr1_start_index
        left_type = self.determineExpressionType()
       
        # Determine type of second expression
        self.index = expr2_start_index
        right_type = self.determineExpressionType()
       
        # Restore position
        self.index = saved_index
       
        # Type checking for comparison operators
        if left_type != "unknown" and right_type != "unknown" and left_type != right_type:
            # Special case: Allow comparison between boolean and integer literals 0 and 1 (but cannot be expressions)
            special_case = False
           
            # Check if one is boolean and the other is integer
            if (left_type == "boolean" and right_type == "integer"):
                # Check if the right side is just a simple 0 or 1 literal with no operations
                temp_idx = self.index
                self.index = expr2_start_index
               
                # Check if the token is a simple integer literal
                token = self.currentToken()
                if token.type == "integer" and token.lexeme in ["0", "1"]:
                    # Look ahead for any operators that would make this a complex expression
                    has_operators = False
                    for i in range(expr2_start_index, saved_index):
                        if i < len(self.tokens) and self.tokens[i].type == "operator" and self.tokens[i].lexeme in ["+", "-", "*", "/"]:
                            has_operators = True
                            break
                   
                    if not has_operators:
                        special_case = True
               
                self.index = temp_idx
            elif (right_type == "boolean" and left_type == "integer"):
                # Check if the left side is just a simple 0 or 1 literal with no operations
                temp_idx = self.index
                self.index = expr1_start_index
               
                # Check if the token is a simple integer literal
                token = self.currentToken()
                if token.type == "integer" and token.lexeme in ["0", "1"]:
                    # Look ahead for any operators that would make this a complex expression
                    has_operators = False
                    for i in range(expr1_start_index, expr2_start_index - 1):  # -1 to exclude the relop
                        if i < len(self.tokens) and self.tokens[i].type == "operator" and self.tokens[i].lexeme in ["+", "-", "*", "/"]:
                            has_operators = True
                            break
                   
                    if not has_operators:
                        special_case = True
               
                self.index = temp_idx
           
            # If not a special case (simple integer 0 or 1 with boolean), then report an error
            if not special_case:
                self.error(f"Type mismatch: You cannot compare {left_type} with {right_type} using {relop_token.lexeme}")


    def parseRelop(self):
        self.printProduction("<Relop> -> == | != | > | < | <= | =>")
       
        token = self.currentToken()
        if token.type == "operator" and token.lexeme in ["==", "!=", ">", "<", "<=", "=>"]:
            self.match("operator", token.lexeme)
        else:
            self.error("Relational operator expected")




    def parseReturnStmt(self):
        self.printProduction("<Return> -> return <Expression> ;")
   
        if not self.match("keyword", "return"):
            return
   
        # Save position before parsing expression to determine its type
        expr_start_index = self.index
   
        self.parseExpression()
   
        # Determine the expression type being returned
        saved_index = self.index
        self.index = expr_start_index
        return_type = self.determineExpressionType()
        self.index = saved_index
   
        # Update the containing function's return type if we're in a function
        # Find the function we're currently in by looking at tokens.
        for i in range(self.index - 1, -1, -1):
            if (i < len(self.tokens) and
                self.tokens[i].type == "identifier" and
                self.tokens[i].lexeme in self.functions and
                i > 0 and self.tokens[i-1].type == "keyword" and
                self.tokens[i-1].lexeme == "function"):
               
                function_name = self.tokens[i].lexeme
                # Update the return type
                if function_name in self.functions:
                    self.functions[function_name]["return_type"] = return_type
                break
   
        if not self.match("separator", ";"):
            self.error("Expected semicolon after return statement")




    def parseAssignment(self):
        self.printProduction("<Assign> -> <Identifier> = <Expression> ;")
   
        var_name = self.currentToken().lexeme
   
        # Check if variable is declared
        if not self.isVariableDeclared(var_name):
            self.error(f"Variable '{var_name}' used before declaration")
            # Continue parsing but flag the error
   
        # Get the variable's declared type
        var_type = self.getVariableType(var_name)
   
        if not self.match("identifier"):
            return
       
        if not self.match("operator", "="):
            return
   
        # Save position before parsing expression
        expr_start_index = self.index
   
        # Parse expression normally
        self.parseExpression()
   
        # Type checking logic
        # Reset to start of expression for type determination
        saved_index = self.index
        self.index = expr_start_index
       
        # Determine the expression type
        expr_type = self.determineExpressionType()
       
        # Restore position
        self.index = saved_index
       
        # Type compatibility check
        if expr_type != "unknown" and var_type != "unknown" and var_type != expr_type:
            # Check if the types are compatible
            if not self.areTypesCompatible(var_type, expr_type):
                self.error(f"Type mismatch: Cannot assign {expr_type} value to {var_type} variable '{var_name}'")
       
        # Get memory address for the variable
        mem_addr = None
        for i, var in enumerate(self.global_vars.keys()):
            if var == var_name:
                mem_addr = self.memAddrList[i]
                break
       
        # Add POPM instruction to store the value into variable's memory location
        if mem_addr is not None:
            self.assemblyList.append(f"POPM      {mem_addr}")
       
        if not self.match("separator", ";"):
            self.error("Expected semicolon after assignment")




    # Removed left recursion in Expression
    def parseExpression(self):
        self.printProduction("<Expression> -> <Term> <ExpressionPrime>")
       
        self.parseTerm()
        self.parseExpressionPrime()




    def parseExpressionPrime(self):
        self.printProduction("<ExpressionPrime> -> + <Term> <ExpressionPrime> | - <Term> <ExpressionPrime> | ε")


        token = self.currentToken()
        if token.type == "operator" and token.lexeme in ["+", "-"]:
            op = token.lexeme
            self.match("operator", op)
   
            # Store position before parsing term
            term_start_index = self.index
       
            # Save current position to determine left operand type
            left_start_index = self.index - 2  # Go back before the operator
       
            self.parseTerm()
       
            # Add the operation instruction
            if op == "+":
                self.assemblyList.append("A")
            else:  # op == "-"
                self.assemblyList.append("S")
       
            # Check for boolean operands
            saved_index = self.index
       
            # Go back to determine left operand type
            self.index = left_start_index
            left_type = self.determineExpressionType()
           
            # Go to term position to determine its type
            self.index = term_start_index
            right_type = self.determineExpressionType()
           
            # Restore position
            self.index = saved_index
           
            # Check for boolean operands on either side
            if left_type == "boolean" or right_type == "boolean":
                self.error(f"Cannot use {op} operator with boolean operands")
               
            self.parseExpressionPrime()
        else:
            self.printProduction("<ExpressionPrime> -> ε")








    def parseTerm(self):
        self.printProduction("<Term> -> <Factor> <TermPrime>")
       
        self.parseFactor()
        self.parseTermPrime()




   
    def parseTermPrime(self):
        self.printProduction("<TermPrime> -> * <Factor> <TermPrime> | / <Factor> <TermPrime> | ε")


        token = self.currentToken()
        if token.type == "operator" and token.lexeme in ["*", "/"]:
            op = token.lexeme
            self.match("operator", op)
   
            # Store position before parsing factor
            factor_start_index = self.index
           
            # Save current position to determine left operand type
            left_start_index = self.index - 2  # Go back before the operator
           
            self.parseFactor()
           
            # Add the operation instruction
            if op == "*":
                self.assemblyList.append("M")
            else:  # op == "/"
                self.assemblyList.append("D")
           
            # Check for boolean operands
            saved_index = self.index
           
            # Go back to determine left operand type
            self.index = left_start_index
            left_type = self.determineExpressionType()
       
            # Go to factor position to determine its type
            self.index = factor_start_index
            right_type = self.determineExpressionType()
           
            # Restore position
            self.index = saved_index
           
            # Check for boolean operands on either side
            if left_type == "boolean" or right_type == "boolean":
                self.error(f"Cannot use {op} operator with boolean operands")
               
            self.parseTermPrime()
        else:
            self.printProduction("<TermPrime> -> ε")








    def parseFactor(self):
        self.printProduction("<Factor> -> <Identifier> | <Number> | ( <Expression> ) | <Function Call>")
       
        token = self.currentToken()
       
        if token.type == "identifier":
            id_name = token.lexeme
            next_token = None if self.index + 1 >= len(self.tokens) else self.tokens[self.index + 1]
           
            # Check if it might be a function call
            if next_token and next_token.type == "separator" and next_token.lexeme == "(":
                self.parseFunctionCall()
            else:
                # Check if variable is declared
                if not self.isVariableDeclared(id_name) and id_name not in self.functions:
                    self.error(f"Variable '{id_name}' used before declaration")
                else:
                    # Get memory address for the variable
                    mem_addr = None
                    for i, var in enumerate(self.global_vars.keys()):
                        if var == id_name:
                            mem_addr = self.memAddrList[i]
                            break
                   
                    # Only add PUSHM if not inside a print statement
                    if mem_addr is not None and not getattr(self, 'in_print', False):
                        self.assemblyList.append(f"PUSHM     {mem_addr}")
               
                self.match("identifier")
               
        elif token.type in ["integer"]:
            # Add PUSHI instruction to push literal integers onto stack
            if not getattr(self, 'in_print', False):
                self.assemblyList.append(f"PUSHI     {token.lexeme}")
            self.match(token.type)
        elif token.type == "separator" and token.lexeme == "(":
            self.match("separator", "(")
            self.parseExpression()
            self.match("separator", ")")
        elif token.type == "keyword" and token.lexeme in ["true", "false"]:
            # Handle boolean literals - convert to integers (0 or 1)
            value = "1" if token.lexeme == "true" else "0"
            if not getattr(self, 'in_print', False):
                self.assemblyList.append(f"PUSHI     {value}")
            self.match("keyword")
        else:
            self.error(f"Unexpected token in factor: {token.lexeme}")
            # Skip the problematic token
            self.nextToken()








    def parseVarDec(self):
        self.printProduction("<Declaration> -> <Qualifier> <IDs> ;")
       
        # Get the type first
        var_type = self.currentToken().lexeme  # integer or boolean
        self.parseQualifier()
       
        # Pass the type to parseIDs
        self.parseIDs(var_type)
       
        if not self.match("separator", ";"):
            self.error("Expected semicolon after variable declaration")




    def parseIDs(self, var_type=None):
        self.printProduction("<IDs> -> <Identifier> <IDsPrime>")
       
        var_name = self.currentToken().lexeme
        if not self.match("identifier"):
            return
           
        if var_type:  # Store type if provided
            self.declareVariable(var_name, var_type)
        else:
            self.declareVariable(var_name, "unknown")
           
        self.parseIDsPrime(var_type)




    def parseIDsPrime(self, var_type=None):
        self.printProduction("<IDsPrime> -> , <Identifier> <IDsPrime> | ε")
       
        if self.currentToken().type == "separator" and self.currentToken().lexeme == ",":
            self.match("separator", ",")
            var_name = self.currentToken().lexeme
            if not self.match("identifier"):
                return
               
            if var_type:  # Store type if provided
                self.declareVariable(var_name, var_type)
            else:  
                self.declareVariable(var_name, "unknown")
               
            self.parseIDsPrime(var_type)
        else:
            self.printProduction("<IDsPrime> -> ε")




    def parseFunctionCall(self):
        self.printProduction("<Function Call> -> <Identifier> ( <Arguments> )")




        function_name = self.currentToken().lexeme




        # Check if function is defined
        if function_name not in self.functions:
            self.error(f"Function '{function_name}' used before declaration")
            if not self.match("identifier"):
                return
            if not self.match("separator", "("):
                return
            self.parseArguments()
            if not self.match("separator", ")"):
                return
            return




        # Get function parameter info
        function_params = self.functions[function_name].get("params", [])




        if not self.match("identifier"):
            return




        if not self.match("separator", "("):
            return




        # Parse arguments and collect their types
        arg_types = self.parseArguments(expected_count=len(function_params))




        # Validate argument count
        if len(arg_types) != len(function_params):
            self.error(f"Function '{function_name}' called with {len(arg_types)} arguments but expects {len(function_params)}")
        else:
            # Validate argument types if we have them
            for i, (arg_type, param) in enumerate(zip(arg_types, function_params)):
                if arg_type != "unknown" and param[1] != "unknown" and arg_type != param[1]:
                    if not self.areTypesCompatible(param[1], arg_type):
                        self.error(f"Type mismatch in function call '{function_name}': argument {i+1} is {arg_type}, but parameter '{param[0]}' expects {param[1]}")




        if not self.match("separator", ")"):
            return




        # Check if this is part of a statement (which needs semicolon)
        if (self.currentToken().type == "separator" and
            self.currentToken().lexeme == ";"):
            self.match("separator", ";")




    def parseArguments(self, expected_count=None):
        self.printProduction("<Arguments> -> <Expression> <ArgumentsPrime> | ε")




        arg_types = []




        if self.currentToken().type != "separator" or self.currentToken().lexeme != ")":
            # Save position to determine expression type
            expr_start_index = self.index




            self.parseExpression()




            # Determine the expression type
            saved_index = self.index
            self.index = expr_start_index
            expr_type = self.determineExpressionType()
            self.index = saved_index




            arg_types.append(expr_type)




            # Parse the rest of the arguments and collect their types
            more_arg_types = self.parseArgumentsPrime(expected_count-1 if expected_count is not None else None)
            arg_types.extend(more_arg_types)
        else:
            self.printProduction("<Arguments> -> ε")
            if expected_count and expected_count > 0:
                self.error(f"Expected {expected_count} arguments but got 0")




        return arg_types




    def parseArgumentsPrime(self, expected_count=None):
        self.printProduction("<ArgumentsPrime> -> , <Expression> <ArgumentsPrime> | ε")




        arg_types = []




        if self.currentToken().type == "separator" and self.currentToken().lexeme == ",":
            self.match("separator", ",")




            # Save position to determine expression type
            expr_start_index = self.index




            self.parseExpression()




            # Determine the expression type
            saved_index = self.index
            self.index = expr_start_index
            expr_type = self.determineExpressionType()
            self.index = saved_index




            arg_types.append(expr_type)




            # parse more arguments
            more_arg_types = self.parseArgumentsPrime(expected_count-1 if expected_count is not None else None)
            arg_types.extend(more_arg_types)
        else:
            self.printProduction("<ArgumentsPrime> -> ε")
            if expected_count and expected_count > 0:
                self.error(f"Too few arguments: expected {expected_count} more")




        return arg_types








# Token class details
class Token:
    def __init__(self, token_type, lexeme, line_number):
        self.type = token_type
        self.lexeme = lexeme
        self.line_number = line_number




def main():
    source = ""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python rat25s_parser.py")
        return
   
    inputfile = sys.argv[1]
    outputfile = "parser_output.txt" if len(sys.argv) < 3 else sys.argv[2]
   
    print(f"Parsing {inputfile}...")
   
    try:
        with open(inputfile, "r") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
   
    print(f"File read successfully, tokenizing...")
    tokens = lexer(source)
    print(f"Found {len(tokens)} tokens, parsing...")
   
    parser = Parser(tokens)
   
    try:
        parser.parseProgram()
        print("Parsing complete")
    except Exception as e:
        print(f"Parsing error: {e}")
   
    try:
        with open(outputfile, "w", encoding="utf-8") as out:
            for line in parser.output_lines:
                out.write(line + "\n")
            out.write("\nSymbol Table:\n")
            out.write(f"{'Identifier':<20}{'MemoryLocation':<20}Type\n")
            for (var_name, var_type), memAddr in zip(parser.global_vars.items(), parser.memAddrList):
                out.write(f"{var_name:<20}{memAddr:<20}{var_type:<20}\n")


            out.write("\nAssembly Code Listing:\n")
            for i, instruction in enumerate(parser.assemblyList):
                out.write(f"{i + 1:<10} {instruction}\n")
                     
        print(f"Output written to {outputfile}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return
   
    if parser.error_count > 0:
        print(f"Parsing completed with {parser.error_count} errors. See {outputfile} for details.")
    else:
        print(f"Parsing completed successfully. Output written to {outputfile}")




if __name__ == "__main__":
    main()



