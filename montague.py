import sys
import time
import nltk
import nltk.data
from nltk import ParentedTree
from stat_parser import Parser, display_tree

def main():
    path = './lexicon.txt'
    f = open(path, 'r')
    lex = loadLexicon(f)

    grammer_file = 'grammer_file.fcfg'
    grammer = nltk.data.load("file:mygrammer.cfg","cfg")
    inp = raw_input("\nPlease provide a sentenced: ")
    sentence = inp.split()
    parser = nltk.RecursiveDescentParser(grammer)
    #parser = Parser()))

    
    print "==== Syntax Tree  ===="
    time.sleep(2);
    try:
        for tree in parser.parse(sentence): tree.pretty_print() #print tree
    except ValueError:
        print "Word not found in grammar file. Please add missing word " + \
                "in the appropriate field"
        return
    # convert tree to parented tree
    try:
        ptree = ParentedTree.convert(tree)
    except UnboundLocalError:
        print "Syntax tree could not be created. Please check that" + \
                " grammar file contains sentence \nstructure or that your" + \
                " input is a valid english sentence."
        return

    baseNodes(ptree, lex)
    traverse(ptree)
    
# --- LAMBDA FUNCTIONS --- 
# lambda conversion
def LC(exp):
    return exp.simplify()

# functional application
def FA(x, y):
    read = nltk.sem.Expression.fromstring
    if x is None:
        return read(y)
    if y is None:
        return read(x)
    else:
        return read('(' + str(x) + ')(' + str(y) + ')')

# non branching node
def NN(x):
    # x is a string. Don't worry about expressions here
    return x

# predicate modification
def PM(alpha, beta):
    read = nltk.sem.Expression.fromstring
    # strip down the original structure and join with and
    return read('\\x.(' + alpha[3:] + ' & ' + beta[3:] + ')')


# this function simply reads the lexical file and stores 
# the information in a dictionary structure
def loadLexicon( f ):
    dict = {}
    for line in f:
        temp = line.split()
        dict[temp[0]] = '_'.join(temp[1:])

    return dict

# this completes the first step of transforming the leaves 
# into their lexical translation
def baseNodes(tree, lex):
    print "==== Inserting Lexical Entries  ===="
    time.sleep(2);
    positions = tree.treepositions('leaves')
    for i in positions:
        if tree[i] in lex:
            tree[i] = lex[tree[i]]
        else:
            print tree[i] + " not in lexicon, please add to lexicon.txt"
            exit
    
    tree.pretty_print()


# This function does much of the heavy lifting
# It traverses the tree top to bottom and decides which 
# lambda function is appropriate to compute on each node
# It then replace the existing syntactic expression with
# the correct semantic expression. It also prints out which # operation is being completed. 
def traverse( tree ):
    try:
        tree.label()
    except AttributeError:
        return
    else:

        # make a copy of the tree
        copy_tree = tree.copy(True)

        # first handle the leaves
        h = 2
        print "==== Non-Branching Node  ===="
        time.sleep(2);
        for s in tree.subtrees(lambda tree: tree.height() == h):
            for t in tree.subtrees(lambda tree: tree.height() == h):
                s.set_label(NN(s.leaves()[0]));
        tree.pretty_print()

        tested = []
        for h in range(1,tree.height()):
            for s in tree.subtrees():
                tested.append(s)
                for t in tree.subtrees(lambda tree: tree.height() == h):
                    if t not in tested:
                        # branching node
                        if (s.parent() == t.parent()):
                            if (s.label()[0] == "\\" and t.label()[0] == "\\"):
                                # predicate modification test
                                # use a copy of original tree to see if the part of speech
                                # of the root and a node are the same. 
                                if (copy_tree[t.treeposition()].label() == copy_tree[t.parent().treeposition()].label()):
                                    print "==== Predicate Modification  ===="
                                    time.sleep(2);
                                    ans = PM(s.label(), t.label())
                                else:
                                    print "==== Functional Application  ===="
                                    time.sleep(2);
                                    ans = FA(s.label(), t.label())
                            elif (s.label()[0] == "\\" and t.label()[0] != "\\"):
                                print "==== Functional Application  ===="
                                time.sleep(2);
                                ans = FA(s.label(), t.label())
                            elif (s.label()[0] != "\\" and t.label()[0] == "\\"):
                                print "==== Functional Application  ===="
                                time.sleep(2);
                                ans = FA(t.label(), s.label())

                            s.parent().set_label(str(ans))
                            tree.pretty_print()
                            # check to see if lambda conversion is necessary
                            if (LC(ans) != ans):
                                print "==== Lambda Conversion ===="
                                time.sleep(2);
                                s.parent().set_label(str(LC(ans)))
                                tree.pretty_print()
                            
                        # non-branching node
                        else:
                            # this is another time NN occurs No need to pause here
                            # because its not that interesting 
                            t.parent().set_label(NN(t.label()))
            # clear buffer
            tested = []


if __name__ == "__main__":
    main()
