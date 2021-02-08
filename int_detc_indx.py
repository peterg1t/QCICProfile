import numpy as np

def int_detc_indx(CorrCounts,FRGN):
    max_l = np.amax(CorrCounts[0:len(CorrCounts) // 2+1])
    max_r = np.amax(CorrCounts[len(CorrCounts) // 2:len(CorrCounts)+1])
    for i in range(0, len(CorrCounts) // 2):  # for the left side of the array
        if CorrCounts[i] <= max_l / 2 and CorrCounts[i + 1] > max_l / 2:
            lh = i + (max_l / 2 - CorrCounts[i]) / (CorrCounts[i + 1] - CorrCounts[i])

    for j in range(len(CorrCounts) // 2, len(CorrCounts)-1):  # for the right side of the array
        if CorrCounts[j] > max_r / 2 and CorrCounts[j + 1] <= max_r / 2:
            rh = j + (CorrCounts[j] - max_r / 2) / (CorrCounts[j] - CorrCounts[j + 1])

    CM = (lh + rh) / 2


    lFRGN = CM + (lh - CM) * FRGN / 100
    rFRGN = CM + (rh - CM) * FRGN / 100
    # print("lFRGN","rFRGN","lh","rh","CM")
    # print(lFRGN,rFRGN,lh,rh,CM)

    lf = int(lFRGN)+1
    rf = int(rFRGN)

    return lf, rf, lFRGN, rFRGN, CM