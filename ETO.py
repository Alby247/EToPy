
import pyeto
from datetime import datetime

def main():
    # https://www.fao.org/3/X0490E/x0490e06.htm#fao%20penman%20monteith%20equation

    #test data 

    #site constants
    altitude=51
    latitude=-34.229167
    windspeed_height=10

    """

    from Mildura airport BOM 
    11/12/2023	10.4	0.0	 	40.8	16.8	74	13	5.32	21.20
    25/12/2023	2.3	    0.0	 	17.9	14.3	100	67	5.37	9.93
    27/12/2023	6.6	    0.8	 	29.9	15.9	100	33	3.26	30.01

    All tested with identical results to BOM website

    Replace this with daily data when live

    """

    tmin=15.9
    tmax=29.9
    rh_min=33
    rh_max=100
    sol_rad=30.01
    WindSpd=3.26

    Year=2023
    Month=12
    Day=25

    #####################################################################################

    #calculated values

    #convert date to day of year
    day_of_year = datetime(Year, Month, Day).timetuple().tm_yday
    #day_of_year = datetime.today().timetuple().tm_yday
    #Note if calculating using yesterdays data, may need to subtract one from day_of_year

    #t is mean of tmax and tmin - needs to be C for svp but convert to K for Eto
    t=(tmin+tmax)/2

    #latitude needs to be in radians
    latitude=pyeto.convert.deg2rad(latitude)

    #estimate avp
    svp_tmin=pyeto.fao.svp_from_t(tmin)
    svp_tmax=pyeto.fao.svp_from_t(tmax)
    avp=pyeto.fao.avp_from_rhmin_rhmax(svp_tmin,svp_tmax,rh_min,rh_max)

    #Several functions required to estimate net_rad
    sol_dec=pyeto.fao.sol_dec(day_of_year)
    sha=pyeto.fao.sunset_hour_angle(latitude, sol_dec) #latitude in radians
    ird=pyeto.fao.inv_rel_dist_earth_sun(day_of_year)
    et_rad=pyeto.fao.et_rad(latitude, sol_dec, sha, ird)
    cs_rad=pyeto.fao.cs_rad(altitude, et_rad)

    tmink=pyeto.convert.celsius2kelvin(tmin)
    tmaxk=pyeto.convert.celsius2kelvin(tmax)

    #tmin and tmax need to be in K for this function
    no_lw_rad=pyeto.fao.net_out_lw_rad(tmink, tmaxk, sol_rad, cs_rad, avp) 

    ni_sw_rad=pyeto.fao.net_in_sol_rad(sol_rad, albedo=0.23)
    net_rad=pyeto.fao.net_rad(ni_sw_rad, no_lw_rad)

    #estimate psy
    atmos_pres=pyeto.fao.atm_pressure(altitude)

    #using 1 as the first parameter is necessary to match BOM ETo
    psy=pyeto.fao.psy_const_of_psychrometer(1, atmos_pres)

    #adjust windspeed to 2m height
    if windspeed_height == 2:
        ws=WindSpd
    else:
        ws=pyeto.fao.wind_speed_2m(WindSpd, windspeed_height)
    
    #estimate svp and delta_svp
    #Note - this is not clear in fao.py, but svp must be the mean of svp at tmax and svp at tmin,
    #not svp of mean t.  Ref. equation 11 and 12 in FAO paper
    svpmax=pyeto.fao.svp_from_t(tmin)
    svpmin=pyeto.fao.svp_from_t(tmax)
    svp=(svpmax+svpmin)/2

    delta_svp=pyeto.fao.delta_svp(t)

    #t needs to be in Kelvin for the Eto function
    t=pyeto.convert.celsius2kelvin(t)

    #Calculate final Eto
    Eto=pyeto.fao.fao56_penman_monteith(net_rad, t, ws, svp, avp, delta_svp, psy, shf=0.0)

    """
    print ("net_rad =", net_rad)
    print ("t = ", t)
    print ("svp = ", svp)
    print ("avp = ", avp)
    print ("delta_svp = ", delta_svp)
    print ("psy = ", psy)
    """
    Eto=round (Eto, 1)

    print ("Eto = ", Eto)

    return Eto

if __name__ == '__main__':
        main()
        
