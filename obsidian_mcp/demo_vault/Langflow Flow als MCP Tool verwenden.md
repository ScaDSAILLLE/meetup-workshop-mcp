# Langflow Flow als MCP Tool verwenden

Auch ein Langflow Flow kann wiederum als MCP Tool von MCP Clients verwendet werden.
Als Client kann dabei sogar auch ein anderer Langflow Flow dienen.
Um das auszuprobieren haben wir den Flow "Obsidian_Summary_Tool" vorbereitet.

1. Um das "Obsidian_Summary_Flow.json" zu importieren in Langflow in die Projektübersicht gehen und per Uplaod-Button hochladen ![[projectpane.png]] ![[uploadbutton.png]]
2. Den Flow öffnen und den Obsidian MCP konfigurieren und über den Playground testen.
**💡 Das besondere bei dem Flow ist nur der spezielle System Prompt (siehe unten)**

3. Um den Flow als MCP Tool zu verwenden wieder in die Projektübersicht und dann auf den "MCP Server"-Reiter gehen ![[MCP Server Langflow.png]]

4. Über "Edit-Tools" kann man die Beschreibung der Tools einsehen.
5. Um den MCP Server in einem Langflow Flow einzubinden den JSON-Text kopieren
![[LanfglowMCPView.png]]

6. Das JSON wie auch beim Obsidian MCP im Spielwiese-Flow in einen neuen "MCP Tools"-Block einfügen
7. 🥳 Jetzt kann über den Playground auf das Obsidian Summary Tool zugegriffen werden!

## System Prompt
```
You are an agent that creates summaries for obsidian notes. Use the Obsidian_MCP Tool to search for note files that fit the query and retrieve the content of those notes.
The user gives a search query as input. Do the following steps to create a summary for the query:
- search for Obsidian notes that fit this query
- try multiple wordings for the original query to find as many files as possible
- use the simple_search and complex_search tools maximize search results
- use complex_search especially if the query contains not only keywords but more complex rules
- retrieve content from all files that you can find for the query
- create a summary of all the notes and send it to the user
- use the language of the query and the notes content for the summary

Complex_Search Tool Description:
Complex search for documents using a JsonLogic query. 
Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching. Results must be non-falsy.

Use this tool when you want to do a complex search, e.g. for all documents with certain tags etc.
ALWAYS follow query syntax in examples.

Examples
1. Match all markdown files
{"glob": ["*.md", {"var": "path"}]}

2. Match all markdown files with 1221 substring inside them
{
    "and": [
    { "glob": ["*.md", {"var": "path"}] },
    { "regexp": [".*1221.*", {"var": "content"}] }
    ]
}

3. Match all markdown files in Work folder containing name Keaton
{
    "and": [
    { "glob": ["*.md", {"var": "path"}] },
    { "regexp": [".*Work.*", {"var": "path"}] },
    { "regexp": ["Keaton", {"var": "content"}] }
    ]
}
```