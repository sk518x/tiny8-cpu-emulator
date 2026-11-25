; Print the first 10 Fibonacci numbers: 0 1 1 2 3 5 8 13 21 34
; Memory: 128 = current number, 129 = next number, 130 = how many are left
        LDA 0
        STA 128
        LDA 1
        STA 129
        LDA 10
        STA 130
loop:
        LDM 128
        OUT             ; print the current number
        ADD 129         ; current + next
        TAB             ; keep that sum safe in B
        LDM 129
        STA 128         ; current = old next
        TBA
        STA 129         ; next = the sum
        LDM 130
        SUBI 1
        STA 130
        JNZ loop
        HLT