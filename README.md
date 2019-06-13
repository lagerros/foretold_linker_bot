- Implement simple DSL to allow users to define the logic they want for the bot to compute based on the variables provided

MVP:
- Input of DSL will be a file provided at command line runtime
- The DSL will be a series of defined functions (SUM, PRODUCT, DIVIDE) and IF THEN logic.
    - Use Lark library
- Basic implementation is a calculator like feature

- Grammer needs to handle samples of distributions, add those together in the appropriate way
    - TODO: Look up how n unequal samples from a PDF can be combined. 


Three parts:
 - General language definition
    - Needs to handle samples of probability distributions
- User defined function (UDF)
    - User, to start, will provide the specific variables that will match
- F2 provided inputs
    - F2 will collect the variables, send them over to the parser, along w/ file location of UDF

        - A, b, c will be sent over with valuws part of the interface 
        - I'll receive samples of XS and YS as an array

