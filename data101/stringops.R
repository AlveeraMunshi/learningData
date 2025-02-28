istring <-'Abqkd123&hhsD'
cat('This checks for capital letters  in the string')
contains_capital <- grepl("[A-Z]", istring)
contains_capital
contains_number <- grepl("[0-9]", istring)
cat('This checks for special characters in the string')
contains_special_char <- grepl("[[:punct:]]", istring)
contains_special_char
cat('This calculates the number of characters in the string')
nchar(istring)


uppercase_only <- gsub("[^A-Z]", "", istring)

# Count the number of uppercase letters
num_uppercase_letters <- nchar(uppercase_only)

# Print the result
cat("Number of capital letters:", num_uppercase_letters, "\n")