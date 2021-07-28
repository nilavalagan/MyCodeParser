from flask import Flask, Response, request
import json
from tree_sitter import Language, Parser
from urllib.request import urlopen

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
@app.route('/hello')
def hello():
    # Render the page
    return "Hello Python!"

@app.route('/parse', methods = ['POST'])
def parse():
    Language.build_library(
      # Store the library in the `build` directory
      'build/my-languages.so',

      # Include one or more languages
      [
        'vendor\\tree-sitter-go',
        'vendor\\tree-sitter-javascript',
        'vendor\\tree-sitter-python',
        'vendor\\tree-sitter-c-sharp',
        'vendor\\tree-sitter-java'
      ]
    )

    #####################################
    ### Input / Output
    #####################################
    supportedLanguages = ["csharp", "python", "java"]
    req_body = request.get_json()
    language = ""
    try:
        language = req_body['language']
    except KeyError:
        # Key is not present
        pass    

    if not language:
        return Response("Invalid request body. \"language\" is a required field", 400)
             
    language = language.lower()
    if language not in supportedLanguages:
        return Response("Input \"language\" " + language + " is not supported", 400)
    
    sourceUrl = ""
    try:
        sourceUrl = req_body['sourceUrl']
    except KeyError:
        # Key is not present
        pass
    
    sourceContent = ""
    try:
        sourceContent = req_body['sourceContent']
    except KeyError:
        # Key is not present
        pass
    
    if not sourceUrl and not sourceContent:
        return Response("Invalid request body. \"sourceUrl\" or \"sourceContent\" should be given", 400)

    ## Read Language and code file content as input from request json string
    ## language = "csharp";
    ## sourceUrl = "https://raw.githubusercontent.com/TheAlgorithms/C-Sharp/master/Algorithms/Encoders/HillEncoder.cs"
    ## sourceContent = "";
        
    #####################################
    ### Global Variables
    #####################################
    outputObject = {"language": language, "sourceUrl": sourceUrl}
    DEBUG_FLAG = True;
    GO_LANGUAGE = Language('build/my-languages.so', 'go')
    JS_LANGUAGE = Language('build/my-languages.so', 'javascript')
    PY_LANGUAGE = Language('build/my-languages.so', 'python')
    CSHARP_LANGUAGE = Language('build/my-languages.so', 'c_sharp')
    Languages = {"python": PY_LANGUAGE, "csharp": CSHARP_LANGUAGE}
    NamespaceQueries = {"python" : "", 
                       "csharp": """(namespace_declaration name: (identifier) @Namespace)""",
                       "java" : ""
                      }
    ClassQueries = {"python" : "", 
                       "csharp": """(class_declaration name: (identifier) @Class)""",
                       "java" : ""
                      }
    MethodQueries = {"python" : "", 
                       "csharp": """(method_declaration name: (identifier) @Method)""",
                       "java" : ""
                      }

    AllQueries = {"namespace": NamespaceQueries, 
                  "class": ClassQueries, 
                  "method": MethodQueries }

    ## Read source file
    sourceContentFromUrl = ""
    if not sourceContent and sourceUrl and sourceUrl.strip():
        ## f = open(sourceLocalPath, "r")  ## this is for local file path
        f = urlopen(sourceUrl)
        sourceContentFromUrl = f.read()
        f.close()        

    parser = Parser()
    ## Set Language based on input language
    languageObject = Languages[language]

    parser.set_language(languageObject)

    ### Parse the code
    if sourceContent and sourceContent.strip():
        contentAsBytes = bytes(sourceContent, 'utf-8') ## sourceContent from input request
    else:
        contentAsBytes = bytes(sourceContentFromUrl) ## sourceContent from input request url

    tree = parser.parse(contentAsBytes)

    root_node = tree.root_node

    ## Pattern matching to identify the objects to return
    for key in AllQueries.keys():
        objectType = key;
        queries = AllQueries[key]
        queryStr = queries[language]

        ## Extract if query string is not empty
        if queryStr and queryStr.strip():
            query = languageObject.query(queryStr)
            captures = query.captures(tree.root_node)
            if DEBUG_FLAG:
                print('#', objectType, ': ', len(captures))
        
            objectNameList = []
            for item in captures:
                treeNode = item[0]
                objectName = contentAsBytes[treeNode.start_byte:treeNode.end_byte].decode("utf-8")
                objectNameList.append(objectName);
                if DEBUG_FLAG:
                    print('Type :', objectType, ', Name: ', objectName)
            outputObject.update({objectType : objectNameList})

    if DEBUG_FLAG:
        print('Enumerated all objects.')
    returnString = json.dumps(outputObject)
    if DEBUG_FLAG:
        print(returnString)    
    return returnString

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
