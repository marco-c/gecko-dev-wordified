import
WebIDL
def
WebIDLTest
(
parser
harness
)
:
    
def
checkArgument
(
argument
QName
name
type
optional
variadic
)
:
        
harness
.
ok
(
isinstance
(
argument
WebIDL
.
IDLArgument
)
                   
"
Should
be
an
IDLArgument
"
)
        
harness
.
check
(
argument
.
identifier
.
QName
(
)
QName
"
Argument
has
the
right
QName
"
)
        
harness
.
check
(
argument
.
identifier
.
name
name
"
Argument
has
the
right
name
"
)
        
harness
.
check
(
str
(
argument
.
type
)
type
"
Argument
has
the
right
return
type
"
)
        
harness
.
check
(
argument
.
optional
optional
"
Argument
has
the
right
optional
value
"
)
        
harness
.
check
(
argument
.
variadic
variadic
"
Argument
has
the
right
variadic
value
"
)
    
def
checkMethod
(
method
QName
name
signatures
                    
static
=
True
getter
=
False
setter
=
False
                    
deleter
=
False
legacycaller
=
False
stringifier
=
False
                    
chromeOnly
=
False
htmlConstructor
=
False
)
:
        
harness
.
ok
(
isinstance
(
method
WebIDL
.
IDLMethod
)
                   
"
Should
be
an
IDLMethod
"
)
        
harness
.
ok
(
method
.
isMethod
(
)
"
Method
is
a
method
"
)
        
harness
.
ok
(
not
method
.
isAttr
(
)
"
Method
is
not
an
attr
"
)
        
harness
.
ok
(
not
method
.
isConst
(
)
"
Method
is
not
a
const
"
)
        
harness
.
check
(
method
.
identifier
.
QName
(
)
QName
"
Method
has
the
right
QName
"
)
        
harness
.
check
(
method
.
identifier
.
name
name
"
Method
has
the
right
name
"
)
        
harness
.
check
(
method
.
isStatic
(
)
static
"
Method
has
the
correct
static
value
"
)
        
harness
.
check
(
method
.
isGetter
(
)
getter
"
Method
has
the
correct
getter
value
"
)
        
harness
.
check
(
method
.
isSetter
(
)
setter
"
Method
has
the
correct
setter
value
"
)
        
harness
.
check
(
method
.
isDeleter
(
)
deleter
"
Method
has
the
correct
deleter
value
"
)
        
harness
.
check
(
method
.
isLegacycaller
(
)
legacycaller
"
Method
has
the
correct
legacycaller
value
"
)
        
harness
.
check
(
method
.
isStringifier
(
)
stringifier
"
Method
has
the
correct
stringifier
value
"
)
        
harness
.
check
(
method
.
getExtendedAttribute
(
"
ChromeOnly
"
)
is
not
None
chromeOnly
"
Method
has
the
correct
value
for
ChromeOnly
"
)
        
harness
.
check
(
method
.
isHTMLConstructor
(
)
htmlConstructor
"
Method
has
the
correct
htmlConstructor
value
"
)
        
harness
.
check
(
len
(
method
.
signatures
(
)
)
len
(
signatures
)
"
Method
has
the
correct
number
of
signatures
"
)
        
sigpairs
=
zip
(
method
.
signatures
(
)
signatures
)
        
for
(
gotSignature
expectedSignature
)
in
sigpairs
:
            
(
gotRetType
gotArgs
)
=
gotSignature
            
(
expectedRetType
expectedArgs
)
=
expectedSignature
            
harness
.
check
(
str
(
gotRetType
)
expectedRetType
                          
"
Method
has
the
expected
return
type
.
"
)
            
for
i
in
range
(
0
len
(
gotArgs
)
)
:
                
(
QName
name
type
optional
variadic
)
=
expectedArgs
[
i
]
                
checkArgument
(
gotArgs
[
i
]
QName
name
type
optional
variadic
)
    
parser
.
parse
(
"
"
"
        
[
Constructor
]
        
interface
TestConstructorNoArgs
{
        
}
;
        
[
Constructor
(
DOMString
name
)
]
        
interface
TestConstructorWithArgs
{
        
}
;
        
[
Constructor
(
object
foo
)
Constructor
(
boolean
bar
)
]
        
interface
TestConstructorOverloads
{
        
}
;
    
"
"
"
)
    
results
=
parser
.
finish
(
)
    
def
checkResults
(
results
)
:
        
harness
.
check
(
len
(
results
)
3
"
Should
be
three
productions
"
)
        
harness
.
ok
(
isinstance
(
results
[
0
]
WebIDL
.
IDLInterface
)
                   
"
Should
be
an
IDLInterface
"
)
        
harness
.
ok
(
isinstance
(
results
[
1
]
WebIDL
.
IDLInterface
)
                   
"
Should
be
an
IDLInterface
"
)
        
harness
.
ok
(
isinstance
(
results
[
2
]
WebIDL
.
IDLInterface
)
                   
"
Should
be
an
IDLInterface
"
)
        
checkMethod
(
results
[
0
]
.
ctor
(
)
"
:
:
TestConstructorNoArgs
:
:
constructor
"
                    
"
constructor
"
[
(
"
TestConstructorNoArgs
(
Wrapper
)
"
[
]
)
]
)
        
harness
.
check
(
len
(
results
[
0
]
.
members
)
0
                      
"
TestConstructorNoArgs
should
not
have
members
"
)
        
checkMethod
(
results
[
1
]
.
ctor
(
)
"
:
:
TestConstructorWithArgs
:
:
constructor
"
                    
"
constructor
"
                    
[
(
"
TestConstructorWithArgs
(
Wrapper
)
"
                      
[
(
"
:
:
TestConstructorWithArgs
:
:
constructor
:
:
name
"
"
name
"
"
String
"
False
False
)
]
)
]
)
        
harness
.
check
(
len
(
results
[
1
]
.
members
)
0
                      
"
TestConstructorWithArgs
should
not
have
members
"
)
        
checkMethod
(
results
[
2
]
.
ctor
(
)
"
:
:
TestConstructorOverloads
:
:
constructor
"
                    
"
constructor
"
                    
[
(
"
TestConstructorOverloads
(
Wrapper
)
"
                      
[
(
"
:
:
TestConstructorOverloads
:
:
constructor
:
:
foo
"
"
foo
"
"
Object
"
False
False
)
]
)
                     
(
"
TestConstructorOverloads
(
Wrapper
)
"
                      
[
(
"
:
:
TestConstructorOverloads
:
:
constructor
:
:
bar
"
"
bar
"
"
Boolean
"
False
False
)
]
)
]
)
        
harness
.
check
(
len
(
results
[
2
]
.
members
)
0
                      
"
TestConstructorOverloads
should
not
have
members
"
)
    
checkResults
(
results
)
    
parser
=
parser
.
reset
(
)
    
parser
.
parse
(
"
"
"
        
interface
TestConstructorNoArgs
{
          
constructor
(
)
;
        
}
;
        
interface
TestConstructorWithArgs
{
          
constructor
(
DOMString
name
)
;
        
}
;
        
interface
TestConstructorOverloads
{
          
constructor
(
object
foo
)
;
          
constructor
(
boolean
bar
)
;
        
}
;
    
"
"
"
)
    
results
=
parser
.
finish
(
)
    
checkResults
(
results
)
    
parser
=
parser
.
reset
(
)
    
parser
.
parse
(
"
"
"
        
[
ChromeConstructor
(
)
]
        
interface
TestChromeConstructor
{
        
}
;
    
"
"
"
)
    
results
=
parser
.
finish
(
)
    
harness
.
check
(
len
(
results
)
1
"
Should
be
one
production
"
)
    
harness
.
ok
(
isinstance
(
results
[
0
]
WebIDL
.
IDLInterface
)
               
"
Should
be
an
IDLInterface
"
)
    
checkMethod
(
results
[
0
]
.
ctor
(
)
"
:
:
TestChromeConstructor
:
:
constructor
"
                
"
constructor
"
[
(
"
TestChromeConstructor
(
Wrapper
)
"
[
]
)
]
                
chromeOnly
=
True
)
    
parser
=
parser
.
reset
(
)
    
parser
.
parse
(
"
"
"
        
interface
TestChromeConstructor
{
          
[
ChromeOnly
]
constructor
(
)
;
        
}
;
    
"
"
"
)
    
results
=
parser
.
finish
(
)
    
harness
.
check
(
len
(
results
)
1
"
Should
be
one
production
"
)
    
harness
.
ok
(
isinstance
(
results
[
0
]
WebIDL
.
IDLInterface
)
               
"
Should
be
an
IDLInterface
"
)
    
checkMethod
(
results
[
0
]
.
ctor
(
)
"
:
:
TestChromeConstructor
:
:
constructor
"
                
"
constructor
"
[
(
"
TestChromeConstructor
(
Wrapper
)
"
[
]
)
]
                
chromeOnly
=
True
)
    
parser
=
parser
.
reset
(
)
    
parser
.
parse
(
"
"
"
        
[
HTMLConstructor
]
        
interface
TestHTMLConstructor
{
        
}
;
    
"
"
"
)
    
results
=
parser
.
finish
(
)
    
harness
.
check
(
len
(
results
)
1
"
Should
be
one
production
"
)
    
harness
.
ok
(
isinstance
(
results
[
0
]
WebIDL
.
IDLInterface
)
               
"
Should
be
an
IDLInterface
"
)
    
checkMethod
(
results
[
0
]
.
ctor
(
)
"
:
:
TestHTMLConstructor
:
:
constructor
"
                
"
constructor
"
[
(
"
TestHTMLConstructor
(
Wrapper
)
"
[
]
)
]
                
htmlConstructor
=
True
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
        
[
Constructor
(
)
         
ChromeConstructor
(
DOMString
a
)
]
        
interface
TestChromeConstructor
{
        
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
Constructor
and
a
ChromeConstructor
"
)
    
#
Test
HTMLConstructor
with
argument
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
(
DOMString
a
)
]
            
interface
TestHTMLConstructorWithArgs
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
HTMLConstructor
should
take
no
argument
"
)
    
#
Test
HTMLConstructor
on
a
callback
interface
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
callback
interface
TestHTMLConstructorOnCallbackInterface
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
HTMLConstructor
can
'
t
be
used
on
a
callback
interface
"
)
    
#
Test
HTMLConstructor
and
Constructor
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
Constructor
             
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
Constructor
and
a
HTMLConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
             
Constructor
]
            
interface
TestHTMLConstructorAndConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
Constructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
             
Constructor
(
DOMString
a
)
]
            
interface
TestHTMLConstructorAndConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
Constructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
Constructor
(
DOMString
a
)
             
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
Constructor
"
)
    
#
Test
HTMLConstructor
and
constructor
operation
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
constructor
and
a
HTMLConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
Throws
]
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
throwing
constructor
and
a
HTMLConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
constructor
(
DOMString
a
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
HTMLConstructor
and
a
constructor
operation
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
Throws
]
              
constructor
(
DOMString
a
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
HTMLConstructor
and
a
throwing
constructor
"
               
"
operation
"
)
    
#
Test
HTMLConstructor
and
ChromeConstructor
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
ChromeConstructor
             
HTMLConstructor
]
            
interface
TestHTMLConstructorAndChromeConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
ChromeConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
             
ChromeConstructor
]
            
interface
TestHTMLConstructorAndChromeConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
ChromeConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
ChromeConstructor
(
DOMString
a
)
             
HTMLConstructor
]
            
interface
TestHTMLConstructorAndChromeConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
             
ChromeConstructor
(
DOMString
a
)
]
            
interface
TestHTMLConstructorAndChromeConstructor
{
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
"
Can
'
t
have
both
a
HTMLConstructor
and
a
ChromeConstructor
"
)
    
#
Test
HTMLConstructor
and
[
ChromeOnly
]
constructor
operation
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
ChromeOnly
]
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
ChromeOnly
constructor
and
a
HTMLConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
Throws
ChromeOnly
]
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
throwing
chromeonly
constructor
and
a
"
               
"
HTMLConstructor
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
ChromeOnly
]
              
constructor
(
DOMString
a
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
HTMLConstructor
and
a
chromeonly
constructor
"
               
"
operation
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
HTMLConstructor
]
            
interface
TestHTMLConstructorAndConstructor
{
              
[
Throws
ChromeOnly
]
              
constructor
(
DOMString
a
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
both
a
HTMLConstructor
and
a
throwing
chromeonly
"
               
"
constructor
operation
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
[
NoInterfaceObject
]
            
interface
InterfaceWithoutInterfaceObject
{
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
a
constructor
operation
on
a
[
NoInterfaceObject
]
"
               
"
interface
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
interface
InterfaceWithPartial
{
            
}
;
            
partial
interface
InterfaceWithPartial
{
              
constructor
(
)
;
            
}
;
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
a
constructor
operation
on
a
partial
interface
"
)
    
parser
=
parser
.
reset
(
)
    
threw
=
False
    
try
:
        
parser
.
parse
(
"
"
"
            
interface
InterfaceWithMixin
{
            
}
;
            
interface
mixin
Mixin
{
              
constructor
(
)
;
            
}
;
            
InterfaceWithMixin
includes
Mixin
        
"
"
"
)
        
results
=
parser
.
finish
(
)
    
except
:
        
threw
=
True
    
harness
.
ok
(
threw
               
"
Can
'
t
have
a
constructor
operation
on
a
mixin
"
)
