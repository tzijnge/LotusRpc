# Compiler warning flags following https://github.com/cpp-best-practices/cppbestpractices/blob/master/02-Use_the_Tools_Available.md#compilers
# Usage: target_set_warnings(<target> <INTERFACE|PUBLIC|PRIVATE>)
function(target_set_warnings target access)
  set(MSVC_WARNINGS
    /W4
    /permissive-
    /w14242   # 'identifier': conversion from 'type1' to 'type2', possible loss of data
    /w14254   # 'operator': conversion from 'type1:field_bits' to 'type2:field_bits', possible loss of data
    /w14263   # 'function': member function does not override any base class virtual member function
    /w14265   # 'classname': class has virtual functions, but its non-trivial destructor is not virtual; instances of this class may not be destructed correctly
    /w14287   # 'operator': unsigned/negative constant mismatch
    /we4289   # nonstandard extension used : 'var' : loop control variable declared in the for-loop is used outside the for-loop scope
    /w14296   # 'operator': expression is always false
    /w14311   # 'variable': pointer truncation from 'type1' to 'type2'
    /w14545   # expression before comma evaluates to a function which is missing an argument list
    /w14546   # function call before comma missing argument list
    /w14547   # 'operator': operator before comma has no effect; expected operator with side-effect
    /w14549   # 'operator': operator before comma has no effect; did you intend 'operator'?
    /w14555   # expression has no effect; expected expression with side-effect
    /w14619   # #pragma warning : there is no warning number 'number'
    /w14640   # 'instance': construction of local static object is not thread-safe
    /w14826   # conversion from 'type1' to 'type2' is sign-extended; may cause unexpected runtime behavior
    /w14905   # wide string literal cast to 'LPSTR'
    /w14906   # string literal cast to 'LPWSTR'
    /w14928   # illegal copy-initialization; more than one user-defined conversion has been implicitly applied
  )

  set(CLANG_WARNINGS
    -Wall
    -Wextra
    -Wshadow
    -Wnon-virtual-dtor
    -Wpedantic
    -Wold-style-cast
    -Wcast-align
    -Wunused
    -Woverloaded-virtual
    -Wconversion
    -Wsign-conversion
    -Wnull-dereference
    -Wdouble-promotion
    -Wformat=2
    -Wimplicit-fallthrough
    -Wundef
    -fno-common
  )

  set(GCC_WARNINGS
    ${CLANG_WARNINGS}
    -Wmisleading-indentation
    -Wduplicated-cond
    -Wduplicated-branches
    -Wlogical-op
    -Wuseless-cast
  )

  if(MSVC)
    set(warnings ${MSVC_WARNINGS})
  elseif(CMAKE_CXX_COMPILER_ID MATCHES ".*Clang")
    set(warnings ${CLANG_WARNINGS})
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(warnings ${GCC_WARNINGS})
  else()
    message(WARNING "target_set_warnings: no flags defined for compiler '${CMAKE_CXX_COMPILER_ID}'")
    return()
  endif()

  target_compile_options(${target} ${access} ${warnings})
endfunction()
