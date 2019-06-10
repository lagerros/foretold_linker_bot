Plan:
- Understand existing graphql schema
    - Done
- Select a question
- Add measurement to that question through the API
    Measure time spent (12:45 pm start)
- Create related questions
    - Initial proxy can be a manual flag to someone to create those initial questions
- Select other questions: if there is a change in those questions measurements, do somehting to the first question.
    - Collection of other questions, when there is an update on those update the main question based on some user defined business logic


Structure of app



curl 'https://api.foretold.io/graphql' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Connection: keep-alive' -H 'DNT: 1' -H 'Origin: https://api.foretold.io' --data-binary '{"query":"# Write your query or mutation here\nquery{\n  measurements(first:10){\n    total\n    edges{\n      node{\n        description\n      }\n    }\n  }\n}"}' --compressed