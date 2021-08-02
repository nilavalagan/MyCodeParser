# MyCodeParser
It is a Pyton REST API project (Visual Studio 2019) that demonstartes the use of [tree-sitter](https://github.com/tree-sitter/tree-sitter) libarary to parse C# and Java code files.

Open the project in Visual Studio, Build and Deploy locally. Once the REST service is up, you can make the below POST request to parse C#/Java code files.

curl --location --request POST 'http://localhost:4449/parse' \
--header 'Content-Type: application/json' \
--data-raw '{
    "language": "java",
    "sourceUrl": "https://raw.githubusercontent.com/n9/pdfclown/master/java/pdfclown.lib/src/org/pdfclown/objects/Cloner.java"
}'

Response returning list of Classes and Methods in the code file.

![image](https://user-images.githubusercontent.com/814563/127814827-9792ffb2-6977-4fcb-9670-cdf04033a484.png)
