from bettermcd import getDatum

for sol in range(1,670):
    d = getDatum(
            lat=0,
            lon=0, 
            sol=sol,
            local_time=15,
            scenario='climatology')

    print(d)
