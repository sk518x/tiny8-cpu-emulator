; Multiply 6 x 7 by adding 6 to a running total, 7 times.
; Memory: 128 = number to add, 129 = how many times are left, 130 = total
; LDA puts a number in A. LDM reads a number from a memory address into A.
        LDA 6
        STA 128
        LDA 7
        STA 129
        LDA 0
        STA 130
loop:
        LDM 130
        ADD 128         ; total + 6
        STA 130
        LDM 129
        SUBI 1          ; one fewer time to go
        STA 129         ; STA leaves the Zero flag alone, so JNZ sees SUBI's result
        JNZ loop
        LDM 130
        OUT             ; prints 42
        HLT