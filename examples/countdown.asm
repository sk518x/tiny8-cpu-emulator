; Count down from 5 to 1, printing each number.
        LDA 5
loop:
        OUT
        SUBI 1          ; A = A - 1, and this sets the Zero flag
        JNZ loop        ; repeat while A is not zero
        HLT