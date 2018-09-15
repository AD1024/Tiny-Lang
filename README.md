# Tiny
A practice-used language; it is not a good programming language, but it will be improved!

# Syntax
## Notice & Rules
- Operator **-** is an arithmetic operator, which means it can only be applied to compute arithmetic expression(s). The *Negation* operator is **~**


## Data Types & Data Binding
- Int
- Double
- Function
- String(working)
And these types can be inferred by the interpreter
To bind data with an identifier, you need to use **:=** symbol instead of **=**, which asserts whether values on its two sides are the same. 
E.g:
```
his_birthday := 1926.0817
print(his_birthday)
```

## If-then-else
Imitating SML, Tiny also uses *If-Then-Else* structure for flow control. Notice that there is an *end* after each block, and if there are still expressions after the block, there should be a semicolon after *end*. 
E.g.
```
he := 1999
if he >= 1990 then
    he := he - 10
else
    he := he + 10
end
print(he) <* Output should be 1989 *>
```

## While Loop
The structure of a *while* loop is:
```
while <condition> do
    <Loop body>
end
```
`<Loop body>` will be executed until `<condition>` equals **False**
E.g.(Counting number of 9 at every digit in an integer)
```
he := 1999
ans := 0
while he > 0 do
    k := he % 10
    if k = 9 then
        ans := ans + 1
    end
    he := he div 10
end
print(ans)
```

## For Loop
The structure of *For* loop is similar to that in C language. 
```
for(<init exp>;<condition>;<post action>) do
    <Loop body>
end
```
`<init exp>`, `condition` and `<post act>` are all optional expressions. You can initialize your cursor outside the definition. However, a regular *For* loop delaration is recommended. 
E.g.(Summing 1 to 10)
```
ans := 0
for(i:=1i<=10;i:=i+1) do
    ans := ans + i
end
print(ans)
```

## Functions
Tiny supports function declaration. The format is:
```
func <Func-name>(<param-list>) =>
    <func-body>
end
```
E.g.(Add two numbers)
```
func add(x,y) =>    
    return x + y
end
print(add(10, 20))
```
Functions support recursive call:
E.g.(Fibonacci number)
```
func fib(x) =>
    if x = 1 orelse x = 2 then
        return x
    else
        return fib(x-1) + fib(x-2)
    end
end
print(fib(6))
```

### High-order function
Functions can be parameters:
E.g.(Wrapper of double-parameter function)
```
func wrapper(fun, x, y) =>
    return fun(x, y)
end
func add(x, y) =>
    return x + y
end
func mul(x, y) =>
    return x * y
end
print(wrapper(add, 1, 10))
print(wrapper(mul, 2, 8))
```

### Lambdas
Now Tiny supports using lambdas:
```
func apply(function, lv, rv) =>
    return {() => return function(lv, rv)} <* Closure *>
end
f := {(x, y) => return x * y }
print(apply({(x, y) => return {() => x * y} }, 3, 4)()())
```
where `f` is a basic lambda assigned the name `f`

### Arrays
Using `array(number_of_elements, init_value=0)` to create arrays:
```
vec := array(100)
arr := array(10, 5)
```
Use subscripting to access and assign value to specific elements in the array
```
vec[0] := 3 * 8
vec[1] := vec[2] + vec[0]
```

# More features coming soon...