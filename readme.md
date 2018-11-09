This is a tutorial style post that walks through using the rpython translation
toolchain to create a simple REPL that executes basic math expressions. By the
end we will be scanning the user's input into tokens, compiling those tokens into
bytecode and running that bytecode in our own virtual machine.

This post is a bit of a diversion while on my journey to create a compliant 
[lox](http://www.craftinginterpreters.com/the-lox-language.html) implementation
using the [rpython translation toolchain](https://rpython.readthedocs.io). The 
majority of this work is a direct rpython translation of the low level C 
guide from Bob Nystrom ([@munificentbob](https://twitter.com/munificentbob)) in the
excellent book [craftinginterpreters.com](https://www.craftinginterpreters.com).


## The road ahead

As this post is rather long I'll break it into a few major sections.

TODO TOC

## A REPL

So if you're a Python programmer you might be thinking this is pretty trivial right?

I mean if we ignore input errors, injection attacks etc couldn't we just do something
like this:

```python
"""
A pure python repl that can parse simple math expressions
"""
while True:
    print(eval(raw_input("> ")))
```

Well it does appear to do the trick:
```
$ python2 section-1-repl/main.py
> 3 + 4 * ((1.0/(2 * 3 * 4)) + (1.0/(4 * 5 * 6)) - (1.0/(6 * 7 * 8)))
3.1880952381
```

So can we just ask rpython to translate this into a binary that runs magically
faster?

Let's see what happens. We need to add 2 functions for rpython to
get its bearings (`entry_point` and `target`) and call the file `targetXXX`:

`section-1-repl/target1.py`

```python
def repl():
    while True:
        print eval(raw_input('> '))


def entry_point(argv):
    repl()
    return 0


def target(driver, *args):
    return entry_point, None
```

Which at translation time gives us this admonishment that accurately tells us
we are trying to call a Python built-in `raw_input` that is unfortunately not 
valid RPython.

```
$ rpython ./1/target1.py
...SNIP...
[translation:ERROR] AnnotatorError: 

object with a __call__ is not RPython: <built-in function raw_input>
Processing block:
 block@18 is a <class 'rpython.flowspace.flowcontext.SpamBlock'> 
 in (target1:2)repl 
 containing the following operations: 
       v0 = simple_call((builtin_function raw_input), ('> ')) 
       v1 = simple_call((builtin_function eval), v0) 
       v2 = str(v1) 
       v3 = simple_call((function rpython_print_item), v2) 
       v4 = simple_call((function rpython_print_newline)) 

```

Ok so we can't use `raw_input` or `eval` but that doesn't faze us. Let's get 
the input from a stdin stream and just print it out (no evaluation).
 

`section-1-repl/target2.py`
```python
from rpython.rlib import rfile

LINE_BUFFER_LENGTH = 1024


def repl(stdin):
    while True:
        print "> ",
        line = stdin.readline(LINE_BUFFER_LENGTH)
        print line


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    try:
        repl(stdin)
    except:
        return 0


def target(driver, *args):
    return entry_point, None

```

Translate `target2.py`:

```
$ rpython --opt=2 1/target2.py
...SNIP...
[Timer] Timings:
[Timer] annotate                       ---  1.2 s
[Timer] rtype_lltype                   ---  0.9 s
[Timer] backendopt_lltype              ---  0.6 s
[Timer] stackcheckinsertion_lltype     ---  0.0 s
[Timer] database_c                     --- 15.0 s
[Timer] source_c                       ---  1.6 s
[Timer] compile_c                      ---  1.9 s
[Timer] =========================================
[Timer] Total:                         --- 21.2 s
```

No errors!? Let's try it out:
```
$ ./target2-c 
1 + 2
>  1 + 2

^C
```

Ahh our first success - let's quickly deal with the flushing fail by using the 
stdout stream directly as well. Let's print out the input in quotes:

```python
from rpython.rlib import rfile

LINE_BUFFER_LENGTH = 1024


def repl(stdin, stdout):
    while True:
        stdout.write("> ")
        line = stdin.readline(LINE_BUFFER_LENGTH)
        print '"%s"' % line.strip()


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    try:
        repl(stdin, stdout)
    except:
        pass
    return 0


def target(driver, *args):
    return entry_point, None
```

Translation works, and the test run too:

```
$ ./target3-c 
> hello this seems better
"hello this seems better"
> ^C
```

So we are in a good place with taking user input and printing output... What about
the whole math evaluation thing we were promised? For that we are can probably leave
our rpython repl behind for a while and connect it up at the end.

## A virtual machine


A virtual machine is the execution engine of our basic math interpreter. It will be very simple,
only able to do simple tasks like addition. I won't go into any depth to describe why we want
a virtual machine, but it is worth noting that many languages including java and python make 
this decision to compile to an intermediate bytecode representation and then execute that with
a virtual machine.  

We are going to keep things very simple. We will have a stack where we can push and pop values,
we will only support floats, and our VM will only implement a few very basic operations.

### OpCodes

In fact our entire instruction set is:

    OP_CONSTANT
    OP_RETURN
    OP_NEGATE
    OP_ADD
    OP_SUBTRACT
    OP_MULTIPLY
    OP_DIVIDE

Since we are targeting rpython we can't use the nice `enum` module from the Python standard
library, so instead we just define a simple class with class attributes.
 
Create a new file `opcodes.py` and add this:

```python
class OpCode:
    OP_CONSTANT = 0
    OP_RETURN = 1
    OP_NEGATE = 2
    OP_ADD = 3
    OP_SUBTRACT = 4
    OP_MULTIPLY = 5
    OP_DIVIDE = 6
```

### Chunks

Ref: 

To start with we need to get some infrastructure in place before we write the VM engine.

Following [craftinginterpreters.com](https://www.craftinginterpreters.com/chunks-of-bytecode.html)
we start with a `Chunk` object which will represent our bytecode. In RPython we have access 
to Python-esq lists so our `code` object will just be a list of OpCode values - which are 
just integers. 

`section-2-vm/chunk.py`
```python
class Chunk:
    code = None

    def __init__(self):
        self.code = []

    def write_chunk(self, byte):
        self.code.append(byte)

    def disassemble(self, name):
        print "== %s ==\n" % name
        i = 0
        while i < len(self.code):
            i = disassemble_instruction(self, i)
```

_From here on I'll only present minimal snippets of code instead of the whole lot, but 
I'll link to the repository with the complete example code. For example the 
various debugging including `disassemble_instruction` isn't particularly interesting
to include verbatim._


We need to check that we can create a chunk and disassemble it. The quickest way to do this
is to use python during development and debugging then every so often try to translate it.

Getting the disassemble part through the rpython translator was a hurdle for me as I
quickly found that many `str` methods such as `format` are not supported, and only very basic
`%` based formatting is supported. I ended up creating helper functions for string manipulation
such as:

```python
def leftpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    return char * (width - l) + string
```

Write a new `entry_point` that creates and disassembles a chunk of bytecode. We can
set the target output name to `vm1` at the same time:

```python
def entry_point(argv):
    bytecode = Chunk()
    bytecode.write_chunk(OpCode.OP_ADD)
    bytecode.write_chunk(OpCode.OP_RETURN)
    bytecode.disassemble("hello world")
    return 0

def target(driver, *args):
    driver.exe_name = "vm1"
    return entry_point, None
```

```
$ ./vm1 
== adding example ==

0000 OP_ADD       
0001 OP_RETURN    
```


### Chunks of data

Ref: http://www.craftinginterpreters.com/chunks-of-bytecode.html#constants

So our bytecode is missing a very crucial element - the values to operate on!

As with the bytecode we can store these constant values as part of the chunk
directly in a list. Each chunk will therefore have a constant data component,
and a code component. 

Edit the `chunk.py` file and add the new instance attribute `constants` as an
empty list, and a new method `add_constant`.

```python
    def add_constant(self, value):
        # See if we already know this constant
        for i, constant in enumerate(self.constants):
            if constant == value:
                return i
        self.constants.append(value)
        return len(self.constants) - 1

```

Now to use this new capability we can modify our example chunk
to write in some constants before the `OP_ADD`:

```python
    bytecode = Chunk()
    constant = bytecode.add_constant(1)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)

    constant = bytecode.add_constant(2)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)

    bytecode.write_chunk(OpCode.OP_ADD)
    bytecode.write_chunk(OpCode.OP_RETURN)

    bytecode.disassemble("adding constants")
```

Which still translates with RPython and when run gives us the following disassembled
bytecode:

```$ ./vm2
== adding example ==

0000 OP_CONSTANT  (00)        '1'
0002 OP_CONSTANT  (01)        '2'
0004 OP_ADD       
0005 OP_RETURN
```

### Emulation  

So those 4 instructions of bytecode combined with the constant value mapping
`00 -> 1.0` and `01 -> 2.0` describes individual steps for our virtual machine
to execute. One major point in favor of defining our own bytecode is we can 
design it to be really simple to execute - this makes the VM really easy to implement.

As I mentioned earlier this virtual machine will have a stack, so let's begin with that.
Now the stack is going to be a busy little beast - as our VM takes instructions like 
`OP_ADD` it will pop off the top two values from the stack, and push the result of adding 
them together back onto the stack. Although dynamically resizing Python lists 
are marvelous, they can be a little slow. (TODO I'm not sure if RPython actually needs this
hint?)

So for (premature) performance optimization reasons we will define a constant sized list
and track the `stack_top` directly. Note how I'm trying to give the rpython translator hints
by adding assertions about the state that I promise the `stack_top` will be in.
 

```python
class VM(object):
    STACK_MAX_SIZE = 256
    stack = None
    stack_top = 0

    def __init__(self):
        self._reset_stack()

    def _reset_stack(self):
        self.stack = [0] * self.STACK_MAX_SIZE
        self.stack_top = 0

    def _stack_push(self, value):
        assert self.stack_top < self.STACK_MAX_SIZE
        self.stack[self.stack_top] = value
        self.stack_top += 1

    def _stack_pop(self):
        assert self.stack_top >= 0
        self.stack_top -= 1
        return self.stack[self.stack_top]

    def _print_stack(self):
        print "         ",
        if self.stack_top <= 0:
            print "[]",
        else:
            for i in range(self.stack_top):
                print "[ %s ]" % self.stack[i],
        print

```


Now we get to the main event, the hot loop. Hope I haven't built it up to much, it is 
actually really simple! We loop until the instructions tell us to stop (`OP_RETURN`),
and dispatch to other simple methods based on the instruction.

```python
    def _run(self):
        while True:
            instruction = self._read_byte()

            if instruction == OpCode.OP_RETURN:
                print "%s" % self._stack_pop()
                return IntepretResultCode.INTERPRET_OK
            elif instruction == OpCode.OP_CONSTANT:
                constant = self._read_constant()
                self._stack_push(constant)
            elif instruction == OpCode.OP_ADD:
                self._binary_op(self._stack_add)    
```


Now the `_read_byte` method will have to keep track of which instruction we are up 
to. So add an instruction pointer (`ip`) to the vm with an initial value of `0`.
Then `_read_byte` is simply getting the next bytecode (int) from the chunk's `code`:

```python
    def _read_byte(self):
        instruction = self.chunk.code[self.ip]
        self.ip += 1
        return instruction
``` 

If the instruction is `OP_CONSTANT` we take the constant's address from the next byte
of the chunk's `code`, retrieve that constant value and add it to the VM's stack.

```python
    def _read_constant(self):
        constant_index = self._read_byte()
        return self.chunk.constants[constant_index]
```

Finally our first arithmetic operation `OP_ADD`, what it has to achive doesn't 
require much explanation: pop two values from the stack, add them together, push the result.
But since a few operations all have the same template we introduce a layer of indirection - 
or abstraction - by introducing a reusable `_binary_op` helper method.

```python
    def _binary_op(self, operator):
        op2 = self._stack_pop()
        op1 = self._stack_pop()
        result = operator(op1, op2)
        self._stack_push(result)

    @staticmethod
    def _stack_add(op1, op2):
        return op1 + op2

``` 

To run our example bytecode the only thing left to do is to pass in the
chunk and call `_run()`:

```python
    def interpret_chunk(self, chunk):
        if self.debug_trace:
            print "== VM TRACE =="
        self.chunk = chunk
        self.ip = 0
        try:
            result = self._run()
            return result
        except:
            return IntepretResultCode.INTERPRET_RUNTIME_ERROR
```

`targetvm3.py` connects the pieces:

```python
def entry_point(argv):
    bytecode = Chunk()
    constant = bytecode.add_constant(1)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)
    constant = bytecode.add_constant(2)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)
    bytecode.write_chunk(OpCode.OP_ADD)
    bytecode.write_chunk(OpCode.OP_RETURN)

    vm = VM()
    vm.interpret_chunk(bytecode)

    return 0
```

Which translates, and when run gives us:

```
./vm3
== VM TRACE ==
          []
0000 OP_CONSTANT  (00)        '1'
          [ 1 ]
0002 OP_CONSTANT  (01)        '2'
          [ 1 ] [ 2 ]
0004 OP_ADD       
          [ 3 ]
0005 OP_RETURN    
3
```

Yes we just computed the result of `1+2`. Pack yourself on the back. 

At this point it is probably valid to check that the translated executable is actually
faster than running our program directly in Python. For this trivial example under 
`Python2`/`pypy` this `targetvm3.py` file runs in 20ms - 90ms region, and the compiled
`vm3` runs in <5ms. Something must be happening during the translation

## Scanning the source

## Compiling expressions

