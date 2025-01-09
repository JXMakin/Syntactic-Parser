import os

# some code and comments below are reused from my part 3
"""
This class creates a node for a tree, keeping track of it's own depth in the tree and its name and potential value
"""
class Node:
    # constructor
    def __init__(self, label, value, depth):
        self.label = label
        self.value = value
        self.depth = depth

    # getters
    def get_label(self):
        return self.label

    def get_value(self):
        return self.value

    def get_depth(self):
        return self.depth
"""
This class holds Node objects in a list. It can print out the parse tree using the list of Nodes. It can add Nodes 
to the list by using a method and delete the last node added
"""
class Tree:
    # constructor
    def __init__(self):
        self.trees = []

    # adds a node to the list of trees
    def add_node(self, node):
        self.trees.append(node)

    # resets the tree by clearing the list
    def reset(self):
        self.trees.clear()
    # deletes the last node in the list
    def delete_last(self):
        del self.trees[-1]

    """
    reads the values in the tree list and prints out their labels to a file. 
    The indentation is based on the depth of each node
    """
    def print_tree(self, file_name):
        file = open(file_name, "a")
        for t in self.trees:
            # if the node has a value other than name (ex. STRING: 123) then it gets printed out as well
            if t.get_value() is not None:
                label = str(t.get_label()) + ": " + str(t.get_value())
            else:
                label = t.get_label()
            indent = " " * t.get_depth()
            file.write(f"{indent}{label}\n")
        file.close()

"""
A Token class keeps track of the token's values, type and if it is a terminal or not (ex. comma)
"""
class Token:
    # constructor
    def __init__(self, token_type, value, boolean):
        self.type = token_type
        self.value = value
        self.is_terminal = boolean
    # getters
    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

    def get_is_terminal(self):
        return self.is_terminal

class Parser:
    # constructor
    def __init__(self, file_name):
        self.token_index = -1
        self.current_token = None
        # all tokens
        self.tokens = []
        self.previous_token = None
        # name of file being written to
        self.file_name = file_name

        # abstract syntax tree
        self.tree = Tree()

    # resets the entire parser
    def reset(self):
        self.token_index = -1
        self.current_token = None
        self.tokens = []
        self.previous_token = None
        self.tree.reset()

    """
     calls the first 2 methods that are needed to start the parsing process
    (read in the tokens from the file and set the current token as the first element in the list)
    """
    def set_up(self, string):
        file = open(self.file_name, "w")
        self.read_file(string)
        self.get_next_token()
        file.close()

    """
    reads the tokens from the input from the file and adds them to a list to be managed by the Parser
    """
    def read_file(self, input_tokens):
        token_type = ""
        value = ""
        in_token = False
        read_comma = False

        for char in input_tokens:
            if char == "<":
                in_token = True
            # reached end of token
            elif char == ">":
                # if a comma wasn't read, the value is set as the token type
                if read_comma is False:
                    value = token_type
                # if only a comma was read, the value and type gets set as comma
                elif read_comma and len(token_type) == 0:
                    token_type = ","
                    value = ","
                # if it was an empty string, it gets set as ""
                elif value == "" or value == " ":
                    value = ""
                # token is a terminal if the token type was also the value
                if token_type == value:
                    boolean = True
                else:
                    boolean = False
                token = Token(token_type, value, boolean)
                self.tokens.append(token)

                token_type = ""
                value = ""
                in_token = False
                read_comma = False
            # ignores comma and says it was read in
            elif char == ",":
                read_comma = True
            elif in_token and char != ",":
                # adds anything before the comma as the token type
                if read_comma is False:
                    token_type += char
                # adds anything after the comma as the token value
                elif read_comma is True:
                    value += char

    """
    Sets the current token as the next token in the list of tokens. If there are no tokens left, it returns false.
    If there are tokens, it returns the true
    It also sets the previous token to be the same value of the current token before getting the next token
    """
    def get_next_token(self):
        self.token_index += 1
        # if there are no tokens left
        if self.token_index >= len(self.tokens):
            return False

        self.previous_token = self.current_token
        self.current_token = self.tokens[self.token_index]
        return True

    """
       This reads in the beginning of a dictionary or list and parses the token accordingly, using the respective
       recursive methods
       """
    def parse(self):
        depth = 0
        # returns nothing if the token was never initialized (empty file)
        if self.current_token is None:
            return
        token = self.current_token.get_type()
        # parses a list
        if token == "[":
            depth = self.add_value_to_tree("list", "[", 0)
            self.parse_list(depth)
        # parses a dictionary
        elif token == "{":
            depth = self.add_value_to_tree("dict", "{", 0)
            self.parse_dict(depth)
       # prints syntax error, doesn't affect tree
        else:
            self.syntax_error("{ or [", depth, False)
        # continues parsing if possible
        if self.get_next_token():
            self.parse()
        else:
            return

    """
    Adds 3 nodes to the tree for the start of a value. It adds 'value', the type of value it is and the terminal to the tree
    and returns the depth of the last node added
    """
    def add_value_to_tree(self, value, leaf, depth):
        self.tree.add_node(Node("value", None, depth))
        self.tree.add_node(Node(value, None, depth+2))
        self.tree.add_node(Node(leaf, None, depth+4))
        return depth + 4
    """
    Adds 3 nodes to the tree for the start of a pair. It adds 'pair', 'value' and 'STRING' to the tree
    and returns depth of where the value is
    """
    def add_pair_to_tree(self, depth):
        self.tree.add_node(Node("pair", None, depth))
        self.tree.add_node(Node("value", None, depth + 2))
        self.tree.add_node(Node("STRING", self.current_token.get_value(), depth + 4))
        return depth + 2

    """
    Prints the syntax error to the file and adds the expected token to the tree unless specified otherwise. 
    It also changes the current token to be the expected token
    """
    def syntax_error(self, expected, depth, edit_tree=True):
        file = open(self.file_name, "a")
        # prints the error
        if self.previous_token is None:
            file.write(f"Syntax error from \"{self.current_token.get_value()}\"Expected {expected}\n")
        else:
            file.write(f"Syntax error from \"{self.previous_token.get_value()} {self.current_token.get_value()}\" "
                   f"token #{self.token_index}-{self.token_index + 1}. Expected {expected}\n")
        # edits the tree and the current token to be the expected token
        if edit_tree:
            self.current_token = Token(expected, expected, True)
            self.tree.add_node(Node(expected, None, depth))

    """
    returns the token that is found before the given parameter token
    """
    def get_prev(self, token):
        index = self.tokens.index(token)
        if index - 1 >= 0:
            return self.tokens[index-1]

    """
    This parses a list. A list has the same number of opening and closing brackets. 
    Every value in the tree is on the same level as the brackets. If an element is a list, or
    dictionary, it calls on those functions, potentially making this recursive. Each value gets added tp the tree
    """
    def parse_list(self, depth):
        squareL_bracket = 1
        squareR_bracket = 0

        get_next = self.get_next_token()
        if not get_next:
            return self.syntax_error("]", depth)

        while True:
            if not get_next:
                # if it's the end of the file and the brackets aren't even, it's an error
                if squareL_bracket != squareR_bracket:
                    self.syntax_error("]", depth)
                break

            # looking for value or end bracket
            if self.previous_token.get_type() == "[" or self.previous_token.get_type() == ",":
                if self.current_token.get_type() in ["NUMBER", "STRING", "BOOLEAN", "NULL"]:
                    self.tree.add_node(Node("value", None, depth))
                    self.tree.add_node(Node(self.current_token.get_type(), self.current_token.get_value(), depth+2))

                # if it's a list parse list
                elif self.current_token.get_type() == "[":
                    sub_depth = self.add_value_to_tree("list", "[", depth)
                    self.parse_list(sub_depth)
                # if it's a dictionary parse dictionary
                elif self.current_token.get_type() == "{":
                    sub_depth = self.add_value_to_tree("dict", "{", depth)
                    self.parse_dict(sub_depth)

                elif self.previous_token.get_type() == "[" and self.current_token.get_type() == "]":
                    squareR_bracket += 1

                # error
                else:
                    # this way it doesn't have a comma before end bracket ,]
                    if self.previous_token.get_type() == "," and self.current_token.get_type() != ",":
                        self.tree.delete_last()

                    self.syntax_error("]", depth,False)


            # needs comma or end bracket
            elif self.previous_token.get_type() in ["NUMBER", "STRING", "BOOLEAN", "NULL", "]", "}"] :
                if self.current_token.get_type() == ",":
                    self.tree.add_node(Node(",", None, depth))

                elif self.current_token.get_type() == "]":
                    squareR_bracket += 1
                # adds a bracket
                else:
                    self.syntax_error("]", depth,False)
                    # if its { or [ it returns and backtracks the current token so a new list or dict can be parsed
                    if self.current_token.get_type() in ["{","["]:
                        self.tree.add_node(Node("]", None, depth))
                        self.token_index -= 1
                        return

            else:
                self.syntax_error("]", depth)
                return

            # ends the list
            if squareL_bracket == squareR_bracket:
                node = Node("]", None, depth)
                self.tree.add_node(node)
                break

            get_next = self.get_next_token()

    """
    This parses a dictionary by using another method to parse each pair. A dictionary is valid it it has equal amounts
    of opening and closing brackets. The values stay on the same level as the brackets 
    """
    def parse_dict(self, depth):
        curlyL_bracket = 1
        curlyR_bracket = 0

        get_next = self.get_next_token()
        if not get_next:
            return self.syntax_error("}", depth)

        while True:
            if not get_next:
                # if it's the end of the file and the brackets aren't even, it's an error
                if curlyL_bracket != curlyR_bracket:
                    self.syntax_error("}", depth)
                break

            # parses the pair
            if self.previous_token.get_type() == "{":
                if self.current_token.get_type() == "STRING":
                    sub_depth = self.add_pair_to_tree(depth)
                    self.parse_pair(sub_depth)

                elif self.current_token.get_type() == "}":
                    curlyR_bracket += 1
                # backtracks the tokens incase it can parse the next thing after adding end bracket
                else:
                    self.syntax_error("}", depth)
                    self.token_index -= 1
                    return

            # parses the pair after the comma
            elif self.previous_token.get_type() == ",":
                if self.current_token.get_type() == "STRING":
                    sub_depth = self.add_pair_to_tree(depth)
                    self.parse_pair(sub_depth)

                elif self.current_token.get_type() == "}":
                    # removes the comma so it doesn't end with ,}
                    self.tree.delete_last()
                    self.syntax_error("STRING", depth, False)
                    # ends dictionary
                    self.tree.add_node(Node("}", None, depth))
                    return
                else:
                    self.syntax_error("STRING", depth,False)
                   # skips through the in valid values until it hits a comma or } to continue properly
                    while get_next:
                        get_next = self.get_next_token()
                        if self.current_token.get_type() == "," or self.current_token.get_type() == "}":
                            break

            # needs a comma or end bracket after a value
            elif self.previous_token.get_type() in ["NUMBER", "STRING", "BOOLEAN", "NULL", "]", "}"]:
                # adds comma
                if self.current_token.get_type() == ",":
                    self.tree.add_node(Node(",", None, depth))

                elif self.current_token.get_type() == "}":
                    curlyR_bracket += 1
                # backtracks the tokens incase it can parse the next thing after adding end bracket
                else:
                    self.syntax_error("}", depth)
                    self.token_index -= 1
                    return
            # backtracks the tokens incase it can parse the next thing after adding end bracket
            else:
                self.syntax_error("}", depth)
                self.token_index -= 1
                return
            # ends the dictionary
            if curlyL_bracket == curlyR_bracket:
                node = Node("}", None, depth)
                self.tree.add_node(node)
                break
            get_next = self.get_next_token()


    """
    this parses a pair value which is found in a dictionary. It adds all values to the tree. If there
    is a list or a dictionary as a value, it will call on those methods, potentially making this recursive.
    """

    def parse_pair(self, depth):
        # pairs has 3 values, it starts off at STRING at 1
        count = 1
        # this value is incase there is an error later on
        before_pair = self.previous_token

        get_next = self.get_next_token()
        # if there isn't another value, remove the unneeded values from the tree
        if not get_next:
            for i in range(3):
                self.tree.delete_last()
            if before_pair.get_type() == ",":
                self.tree.delete_last()

            self.syntax_error(":", depth, False)
            self.current_token = before_pair
            self.previous_token = self.get_prev(before_pair)

        # parses the pair
        while True:
            count += 1
            # if there isn't another value, remove the unneeded values from the tree
            if not get_next:
                for i in range(4):
                    self.tree.delete_last()
                if before_pair.get_type() == ",":
                    self.tree.delete_last()
                self.syntax_error("VALUE", depth, False)
                if before_pair.get_type() != ",":
                    self.current_token = before_pair
                    self.previous_token = self.get_prev(before_pair)
                return

            elif count == 2:
                # needs a : after the key
                if self.previous_token.get_type() == "STRING" and self.current_token.get_type() == ":":
                    self.tree.add_node(Node(":", None, depth))
                # adds a : to the tree so it can parse normally
                else:
                    self.syntax_error(":", depth, False)
                    self.tree.add_node(Node(":", None, depth))

                    self.previous_token = Token(":", ":",False)
                    continue

            elif count == 3:
                # adding a value to the tree
                if self.previous_token.get_type() == ":":
                    if self.current_token.get_type() in ["NUMBER", "STRING", "BOOLEAN", "NULL"]:
                        self.tree.add_node(Node("value", None, depth))
                        self.tree.add_node(
                            Node(self.current_token.get_type(), self.current_token.get_value(), depth + 2))

                    # calls on the method to parse a list
                    elif self.current_token.get_type() == "[":
                        sub_depth = self.add_value_to_tree("list", "[", depth)
                        self.parse_list(sub_depth)

                    # calls on the method to parse a dictionary
                    elif self.current_token.get_type() == "{":
                        sub_depth = self.add_value_to_tree("dict", "{", depth)
                        self.parse_dict(sub_depth)
                        
                    # remove the pair from the tree since the pair is invalid
                    else:
                        self.syntax_error("VALUE", depth, False)
                        for i in range(4):
                            self.tree.delete_last()
                        if before_pair.get_type() != ",":
                            self.current_token = before_pair
                            self.previous_token = self.get_prev(before_pair)

                return

            get_next = self.get_next_token()





    """
    This prints the syntax tree that was created with any of the error corrections in place
    """
    def print(self):
        self.tree.print_tree(self.file_name)

"""
main function that uses the parser to parse the JSON tokens in the different files. It prints
the syntax tree to its own file with the errors that may have occurred
"""
def main():
    files = input("How many files are there? ")
    for i in range(1, int(files) + 1):
        # reads file
        file_name = f"input{i}.txt"
        # creates output file
        output_name = f"output{i}.txt"
        # reads file
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                input_string = file.read().strip()

                # parses
                parser = Parser(output_name)
                parser.set_up(input_string)
                parser.parse()

                parser.print()
                print(f"End of File {i}\n")

        else:
            print(f"{file_name}: File not found")

# runs main class
if __name__ == "__main__":
    main()
