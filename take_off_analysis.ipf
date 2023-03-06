#pragma rtGlobals=1	

////////////////////////////////////////////////////////////
///////////////////////いろいろ使えるコマンド///////////////
///////////////////////////////////////////////////////////

//2方向のドップラー速度から速度の絶対値を求める
function DPspeed()
	wave s2east,s2north,s2east2,s2north2
	duplicate/O s2north DPspd
	DPspd = sqrt((s2east)^2 + (s2north)^2)
	if(waveexists(s2east2)==1)	
		duplicate/O s2north2 DPspd2
		DPspd2 = sqrt((s2east2)^2 + (s2north2)^2)
	endif
end


//2方向のドップラー速度から進行方向を求める
function DPdirection()
	wave s2east,s2north,s2east2,s2north2
	duplicate/O s2north DPdir
	DPdir = atan2(s2north,s2east)
	if(waveexists(s2east2)==1)	
		duplicate/O s2north2 DPdir2
		DPdir2 = atan2(s2north2,s2east2)
	endif
end

//方向の平均値を求める(in:deg out:deg)
function circular_mean(thewave)
	wave thewave
	variable xvalue = 0
	variable yvalue = 0
	variable i = 0
	variable the_mean
	do
		xvalue += cos(thewave[i]*pi/180)
		yvalue += sin(thewave[i]*pi/180)	
		i += 1
	while(i<numpnts(thewave))
	
	the_mean = atan2(yvalue,xvalue)*180/pi
	
	if(the_mean<0)
		the_mean += 360
	endif
	return the_mean
end

//速度の絶対値の変化を移動平均する
function spdavg()
	wave DPspd, DPspd2
	variable i = 0
	variable range = 20 //mooving avrage window
	duplicate/O DPspd DPspd_avg
	do
		DPspd_avg[i] = sum(DPspd,pnt2x(DPspd,i),pnt2x(DPspd,i+range))/range
		i += 1
	while(i<numpnts(DPspd)-range)
	if(waveexists(DPspd2)==1)
		duplicate/O DPspd2 DPspd_avg2
		i = 0
		do
			DPspd_avg2[i] = sum(DPspd2,pnt2x(DPspd2,i),pnt2x(DPspd2,i+range))/range
			i += 1
		while(i<numpnts(DPspd2)-range)
	endif
	
end

//axの分散を計算する
function axvar(axwave)
	wave axwave
	variable i = 0
	variable range = 50
	duplicate/O axwave ax_vari
	do
		ax_vari[i] = variance(axwave,pnt2x(axwave,i),pnt2x(axwave,i+range))
		i += 1
	while(i<numpnts(axwave)-range)
end

//3成分のベクトル長を計算する
function sqrt3(wave_x, wave_y, wave_z,name_s3)
	wave wave_x, wave_y, wave_z
	string name_s3
	duplicate/O wave_x $(name_s3)
	wave wave_s3 = $(name_s3)
	wave_s3 = sqrt((wave_x)^2 + (wave_y)^2 + (wave_z)^2)
end

//waveの最後に値をひとつ追加
Function AppendValue(thewave, thevalue)
    Wave thewave
    Variable thevalue
    Redimension/D/N=(numpnts(thewave)+1) thewave
    thewave [numpnts(thewave)] = thevalue
End

//Ninja2台装着したワタリアホウドリ用　ロードしたwave全ての名前の後に2をつける
function name2()
	wave accuracyH, accuracyV, alt, ax, ay, az, lat, long, mx, my, mz, pr
	wave s2down, s2east, s2north, temp, vx, vy, vz
	variable i = 0
	string waves = WaveList("*",";","")
	string thewavename
	do
		thewavename = StringFromList(i, waves)
		wave thewave = $(thewavename)
		rename thewave $(thewavename+"2")
		i += 1
	while(i<ItemsInList(waves))
end

//Ninja2台装着したワタリアホウドリ用　ロードしたwave全ての名前の後ろから2をとる
function name_delete_2()
	wave accuracyH2, accuracyV2, alt2, ax2, ay2, az2, lat2, long2, mx2, my2, mz2, pr2
	wave s2down2, s2east2, s2north2, temp2, vx2, vy2, vz2
	variable i = 0
	string waves = WaveList("*",";","")
	string thewavename
	do
		thewavename = StringFromList(i, waves)
		wave thewave = $(thewavename)
		rename thewave $(RemoveEnding(thewavename))
		i += 1
	while(i<ItemsInList(waves))
end


//duplicate /O/R=[pcsr(A),pcsr(B)] ax ax_test
//Duplicate/O ax_test, filtered_ax_test; DelayUpdate
//Make/O/D/N=0 coefs; DelayUpdate
//FilterFIR/DIM=0/LO={0.08,0.085,151}/HI={0.045,0.05,151} filtered_ax_test
//axvar(filtered_ax_test)


////////////////////////////////////////////////////////////
///////////////////////飛び立ち解析系/////////////////////////
///////////////////////////////////////////////////////////


//全部やる
function all()
//	DPspeed()
//	spdavg()
//	EthoUTM()
	find_takingoff()
	wind_estimate()
	wave_estimate()
	if(stringmatch(igorinfo(1),"1*") == 1 || stringmatch(igorinfo(1),"2*") == 1)
		detect_running()
	else
		detect_running_wa()
	endif
	TO_dir_estimate2()
	running_prop()
	top_speed()
	flapping_num()
	flapping_num2()
	save_takeoff_CSV()
end

//部分的にやる
function partial()
	flapping_num()
	save_takeoff_CSV()
end


//速度変化から大まかな飛び立ち時刻を推定して、加速度を使ってピンポイントで飛び立ち時刻を求める
Function find_takingoff() //absolute delta of az　for 0.1 sec > 10 ⇒　taking off
    Wave DPspd, DPspd2
    wave az, az2
    wave DPspd_avg, DPspd_avg2
    Variable i = 0
    variable j
    variable k
    variable l
    variable m
	 variable speed_thresh
	 
	 if(stringmatch(igorinfo(1),"1*") == 1 || stringmatch(igorinfo(1),"2*") == 1)
	 	speed_thresh = 2
	 else
	 	speed_thresh = 4
	 endif
	 
	 for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	 if(m == 0)
	 	duplicate/O DPspd takingoff_point_kari
	 	takingoff_point_kari = 0
	 	duplicate/O DPspd_avg speed
	 	duplicate/O az accel
	 endif
	 
	 if(m == 1)
	 	if(waveexists(DPspd2)==1)
	 		duplicate/O DPspd2 takingoff_point_kari
	 		takingoff_point_kari = 0
	 		duplicate/O DPspd_avg2 speed
	 		duplicate/O az2 accel
	 		i = 0
	 	else
	 		break
	 	endif
	 endif
	 
	 
    do
    	//30s landing and 30s fling ⇒　take-off1
    	if(wavemax(speed,pnt2x(speed,i-150),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+150))>=speed_thresh)
    		
    		l = 0 // loop num
    		j = x2pnt(accel,pnt2x(speed,i-1))
    		do
    			if(wavemax(accel,pnt2x(accel,j),pnt2x(accel,j+10))-wavemin(accel,pnt2x(accel,j),pnt2x(accel,j+10))>10)
    				k = x2pnt(speed,pnt2x(accel,j))
    				takingoff_point_kari[k] = 1
    				l = 1000 //break loop
    			endif
    			j += 1
    			l += 1
    		while(l<300)

    	endif
    	
    	//20m 10s landing and 30s fling ⇒　take-off2
//    	if(wavemax(speed,pnt2x(speed,i-6050),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+150))>=speed_thresh)
    	if(wavemax(speed,pnt2x(speed,i-4550),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+150))>=speed_thresh)
    	
    		l = 0 // loop num
    		j = x2pnt(accel,pnt2x(speed,i-1))
    		do
    			if(wavemax(accel,pnt2x(accel,j),pnt2x(accel,j+10))-wavemin(accel,pnt2x(accel,j),pnt2x(accel,j+10))>10)
    				k = x2pnt(speed,pnt2x(accel,j))
    				takingoff_point_kari[k] = 2
    				l = 1000 //break loop
    			endif
    			j += 1
    			l += 1
    		while(l<300)
    	endif
    	
    	//30s landing and 5m 10s fling ⇒　take-off3
    	if(wavemax(speed,pnt2x(speed,i-150),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+1550))>=speed_thresh)
    		
    		l = 0 // loop num
    		j = x2pnt(accel,pnt2x(speed,i-1))
    		do
    			if(wavemax(accel,pnt2x(accel,j),pnt2x(accel,j+10))-wavemin(accel,pnt2x(accel,j),pnt2x(accel,j+10))>10)
    				k = x2pnt(speed,pnt2x(accel,j))
    				takingoff_point_kari[k] = 3
    				l = 1000 //break loop
    			endif
    			j += 1
    			l += 1
    		while(l<300)
    	endif
    	
    	//20m 10s landing and 5m 10s fling ⇒　take-off4
//    	if(wavemax(speed,pnt2x(speed,i-6050),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+1550))>=speed_thresh)
    	if(wavemax(speed,pnt2x(speed,i-4550),pnt2x(speed,i))<speed_thresh && wavemin(speed,pnt2x(speed,i+1),pnt2x(speed,i+1550))>=speed_thresh)
    		l = 0 // loop num
    		j = x2pnt(accel,pnt2x(speed,i-1))
    		do
    			if(wavemax(accel,pnt2x(accel,j),pnt2x(accel,j+10))-wavemin(accel,pnt2x(accel,j),pnt2x(accel,j+10))>10)
    				k = x2pnt(speed,pnt2x(accel,j))
    				takingoff_point_kari[k] = 4
    				l = 1000 //break loop
    			endif
    			j += 1
    			l += 1
    		while(l<300)
    	endif
    	    	
    	i += 1
    while(i<numpnts(speed)-200)
	// 　最初の20分以内は波浪観測しない
    i = 0
    do
    	if(takingoff_point_kari[i]==2)
    		takingoff_point_kari[i]=1
    		i = 6051 //break
    	endif
    	
    	if(takingoff_point_kari[i]==4)
    		takingoff_point_kari[i]=3
    		i = 6051 //break
    	endif
    	i += 1
    while(i<6051)
    
	// 　最後の5分は風観測しない
    i = numpnts(takingoff_point_kari)-1550
    do
    	if(takingoff_point_kari[i]==3)
    		takingoff_point_kari[i]=1
    		i = numpnts(takingoff_point) //break
    	endif
    	
    	if(takingoff_point_kari[i]==4)
    		takingoff_point_kari[i]=2
    		i = numpnts(takingoff_point_kari) //break
    	endif
    	i += 1
    while(i<numpnts(takingoff_point_kari))
    
	// 　オオナギは最初の飛び立ちデータは営巣地や船からの飛び立ちなのでなにも観測しない
	
	if(stringmatch(igorinfo(1),"1*") == 1 || stringmatch(igorinfo(1),"2*") == 1)
		i = 0
		do
    		if(takingoff_point_kari[i]!=0)
    			takingoff_point_kari[i]=0
    			i = numpnts(takingoff_point_kari) //break
    		endif
    		i += 1
    	while(i<numpnts(takingoff_point_kari))  
    endif
    
    // 　GPSを補足していない場合前5分と後20分のデータは使わない
    i = 0
    do
    	if(i>6001 && (numtype(speed[i-6000])==2||numtype(speed[i+6000])==2))
    		takingoff_point_kari[i] = 0
    	endif
    	i += 1
    while(i<numpnts(speed)-6000)
    
    // 　1818030は一定期間GPSの異常がある
    string filename = igorinfo(1)
    if(stringmatch(igorinfo(1),"1818030") == 1)
    	takingoff_point_kari[122132,153388] = 0
    endif
    
    if(m == 0)
    	duplicate/O takingoff_point_kari takingoff_point
    elseif(m == 1)
    	duplicate/O takingoff_point_kari takingoff_point2
    endif
    
    endfor //Ninjaを2つ装着したワタリ用のループ終わり
    
    killwaves speed, accel, takingoff_point_kari
End


//飛行速度から風速と風向を求める(modifyied after Yonehara et al. 2016)
function wind_estimate()
	wave UTM_x_Dir, UTM_x_Dir2
	wave DPspd
	wave takingoff_point
	wave each_fitting_wave
	make/O/N=0 wind_dir_list
	make/O/N=0 wind_spd_list
	make/O/N=0 AIC_list
	variable wind_dir
	variable wind_spd
	variable sinaic
	variable linaic
	
	Variable i = 0
	Variable j = 1
	variable m
	string fitting_wave_name
	string residual_wave_name
	string flight_spd_name
	string flight_dir_name
	
	
	for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	if(m == 0)
		duplicate/O UTM_x_Dir UTM_x_Dir_rad
		UTM_x_Dir_rad = pi*UTM_x_Dir/180
		duplicate/O DPspd speed
		duplicate/O takingoff_point TO_P
	endif
	 
	if(m == 1)
		if(waveexists(UTM_x_Dir2)==1)
			duplicate/O UTM_x_Dir2 UTM_x_Dir_rad
			UTM_x_Dir_rad = pi*UTM_x_Dir/180
			duplicate/O DPspd2 speed
			duplicate/O takingoff_point2 TO_P
			i = 0
	 	else
	 		break
		endif
	endif
	
	
	do
		if(TO_P[i]==3 || TO_P[i]==4)
			
			flight_spd_name = "flight_spd_" + igorinfo(1)+ "_" + num2str(j) //igorinfo(1) = experiment file name
			flight_dir_name = "flight_dir_" + igorinfo(1)+ "_" + num2str(j)
			
			duplicate/O/R=[i+25,i+1525] speed $(flight_spd_name) //5min windspeed, cutoff first 25points (5sec)
			duplicate/O/R=[i+25,i+1525] UTM_x_Dir_rad $(flight_dir_name)
			
			wave flight_spd = $(flight_spd_name)
			wave flight_dir = $(flight_dir_name)
			
			
			K2 = 1;
			CurveFit/Q/H="0010" sin flight_spd /X=flight_dir/R  // sine fitting
//			print K0,K1,K2,K3
//			WaveStats/Q fit_DPspd
//			wind_dir = V_minloc*180/pi  // 0 deg north
// 			wind_spd = (V_max - V_min)/2
// 			if(K1>0)
// 				wind_dir = (pi/2 - mod(K3,2*pi))  // 0 deg north
// 			else
// 				wind_dir = (-pi/2 - mod(K3,2*pi))
// 			endif
// 			
// 			if(wind_dir<0)
// 				wind_dir += 2*pi
// 			endif
// 			
// 			wind_spd = abs(K1)
 			
 			make/O/N=6280 fitting_wave
 			SetScale/P x 0,0.001,"", fitting_wave
 			fitting_wave = K0 + K1*sin(x + K3)
			WaveStats/Q fitting_wave
			wind_dir = V_minloc*180/pi  // 0 deg north
 			wind_spd = (V_max - V_min)/2
 			

 			
 			fitting_wave_name = "fitting_wave_"+ igorinfo(1)+ "_" + num2str(j)
 			duplicate/O fitting_wave $(fitting_wave_name)
 			wave each_fitting_wave = $(fitting_wave_name)
 			
 			appendvalue(wind_dir_list,wind_dir)
			appendvalue(wind_spd_list,wind_spd)
 			
 			//AICを比較する部分
			wave Res_flight_spd = $("Res_flight_spd_" + igorinfo(1)+ "_" + num2str(j))
			duplicate/O Res_flight_spd res //Procedureの冒頭でrtGlobals=1を宣言したのでリファレンス無しでRes_を呼び出せる
			res = Res_flight_spd^2
			
			sinaic = numpnts(res)*((log(2*pi*sum(res)/numpnts(res))/log(e))+1)+2*(1+3)
			
			
			killwaves fitting_wave
			

			CurveFit/Q/H="00" line flight_spd /X=flight_dir/R
			
			wave Res_flight_spd = $("Res_flight_spd_" + igorinfo(1)+ "_" + num2str(j))
			duplicate/O Res_flight_spd res
			res = Res_flight_spd^2
			linaic = numpnts(res)*((log(2*pi*sum(res)/numpnts(res))/log(e))+1)+2*(0+2)
			
			if(sinaic <= linaic-2)
				appendvalue(AIC_list,1)
			else
				appendvalue(AIC_list,0)//AICがそぐわないものを消すのは後
			endif

			
		elseif(TO_P[i]==1 || TO_P[i]==2)
 			appendvalue(wind_dir_list,Nan)
			appendvalue(wind_spd_list,Nan)
			appendvalue(AIC_list,Nan)
		endif
		
		if(TO_P[i]!=0)
			j += 1
		endif
		
		killwaves each_fitting_wave,Res_flight_spd,flight_spd,flight_dir,res
		
		i += 1
	while(i<numpnts(takingoff_point)-1525)
	
	endfor //Ninjaを2つ装着したワタリ用のループ終わり
	
	killwaves UTM_x_Dir_rad, speed, TO_P
	
end


//助走の開始から終わりまでの間の進行方向の平均から飛び立ちの方向を求める TO_dir_list2
function TO_dir_estimate2()
	wave UTM_x_Dir, UTM_x_Dir2
	wave running_mask_new, running_mask_new2
	make/O/N=0 TO_dir_list2
	variable start_running
	variable end_running
	Variable i = 1
	variable j = 0
	variable m
	
	for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	if(m == 0)
		duplicate/O UTM_x_Dir direction
		duplicate/O running_mask_new mask
	endif
	 
	if(m == 1)
		if(waveexists(UTM_x_Dir2)==1)
			duplicate/O UTM_x_Dir2 direction
			duplicate/O running_mask_new2 mask
			i = 1
	 	else
	 		break
		endif
	endif
	
	do
		if(mask[i]-mask[i-1] == 1)
			start_running = i
			j = 0
			do
				if(mask[i+j]-mask[i+j-1] == -1)
					end_running = i+j-1
					break
				endif
				j += 1
			while(j<1000)
			
			duplicate/O/R=(pnt2x(mask,start_running),pnt2x(mask,end_running)) direction TO_dir5
			appendvalue(TO_dir_list2,circular_mean(TO_dir5))			
			i = i+j
		endif
		i += 1
	while(i<numpnts(mask))
	
	endfor //Ninjaを2つ装着したワタリ用のループ終わり
	
	killwaves TO_dir5, direction, mask
end

//pythonから移植したコードを使って飛び立ち直前の波浪を求める
function wave_estimate()
	wave alt, alt2
	wave s2east, s2east2
	wave s2north, s2north2
	wave takingoff_point, takingoff_point2

	make/O/N=0 sgh_list
	make/O/N=0 sgp_list
	make/O/N=0 sgd_list
	
	string twenty_alt_name
	string twenty_s2east_name
	string twenty_s2north_name
	
	Variable i = 0
	Variable j = 1
	variable m
	
	variable sgh
	variable sgp
	variable sgd_math
	variable sgd_climate
	
	for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	if(m == 0)
		duplicate/O alt altitude
		duplicate/O s2east speed_E
		duplicate/O s2north speed_N
		duplicate/O takingoff_point TO_P
	endif
	 
	if(m == 1)
		if(waveexists(UTM_x_Dir2)==1)
			duplicate/O alt2 altitude
			duplicate/O s2east2 speed_E
			duplicate/O s2north2 speed_N
			duplicate/O takingoff_point2 TO_P
			i = 0
	 	else
	 		break
		endif
	endif
	
	do		
		if(TO_P[i]==2 || TO_P[i]==4)
			
			twenty_alt_name = "twenty_alt_" + igorinfo(1)+ "_" + num2str(j) //igorinfo(1) = experiment file name
			twenty_s2east_name = "twenty_s2east_" + igorinfo(1)+ "_" + num2str(j)
			twenty_s2north_name = "twenty_s2north_" + igorinfo(1)+ "_" + num2str(j)
			
//			duplicate/O/R=[i-6025,i-25] altitude $(twenty_alt_name) 
//			duplicate/O/R=[i-6025,i-25] speed_E $(twenty_s2east_name)
//			duplicate/O/R=[i-6025,i-25] speed_N $(twenty_s2north_name)
			
			duplicate/O/R=[i-4525,i-25] altitude $(twenty_alt_name) 
			duplicate/O/R=[i-4525,i-25] speed_E $(twenty_s2east_name)
			duplicate/O/R=[i-4525,i-25] speed_N $(twenty_s2north_name)
			
			wave twenty_alt = $(twenty_alt_name) 
			wave twenty_s2east = $(twenty_s2east_name)
			wave twenty_s2north = $(twenty_s2north_name)
			
			FilterFIR/DIM=0/HI={0.012,0.016,2000} twenty_alt
			
 			calc_ocean_wave_para(twenty_alt, twenty_s2east, twenty_s2north)
 			
			wave result
 			appendvalue(sgh_list,result[0]) //sig height
 			appendvalue(sgp_list,result[1]) //sig period
 			appendvalue(sgd_list,result[3]) //sig direction(deg)
 			
 		elseif(TO_P[i]==1 || TO_P[i]==3)
 			appendvalue(sgh_list,Nan)
			appendvalue(sgp_list,Nan)
			appendvalue(sgd_list,Nan)
		endif
		
		if(TO_P[i]!=0)
			j += 1
		endif

		i += 1
		
		killwaves twenty_alt, twenty_s2east, twenty_s2north
		
	while(i<numpnts(takingoff_point))
	
	killwaves result,twenty_alt, twenty_s2east,twenty_s2north, altitude, speed_E, speed_N, TO_P

	endfor //Ninjaを2つ装着したワタリ用のループ終わり
	
	killwaves result,twenty_alt, twenty_s2east,twenty_s2north, altitude, speed_E, speed_N, TO_P
end


//助走を検出する　ワタリ
function detect_running_wa()
	wave takingoff_point, takingoff_point2
	wave ax, ax2
	Variable i = 0
	variable j = 0
	variable m
	variable reverse_i = 1
	variable range = 50
	variable start_run
	variable end_run
	variable running_time
	make/O/N=0 running_time_list 
	
	
	for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	if(m == 0)
		duplicate/O ax accel
		duplicate/O takingoff_point TO_P
		duplicate/O ax running_mask_kari
		running_mask_kari = 0
	endif
	 
	if(m == 1)
		if(waveexists(UTM_x_Dir2)==1)
			duplicate/O ax2 accel
			duplicate/O takingoff_point2 TO_P
			duplicate/O ax2 running_mask_kari
			running_mask_kari = 0
			i = 0
	 	else
	 		break
		endif
	endif
	
	do
		if(TO_P[i]!=0)
			variable kiritori_hajime = x2pnt(accel,pnt2x(TO_P,i)) - 200 //2s before taingoff_point
			variable kiritori_owari  = kiritori_hajime + 1500
			
			duplicate/O/R=[kiritori_hajime, kiritori_owari] accel ax_filtered
//			FilterFIR/DIM=0/LO={0.125,0.13,151}/HI={0.07,0.075,151} ax_filtered //old filter → running_mask
			FilterFIR/DIM=0/LO={0.245,0.25,151}/HI={0.091,0.096,151} ax_filtered //new filter detecting HiFreq noise → running_mask_new
//			FilterFIR/DIM=0/LO={0.04,0.045,151}/HI={0.02,0.025,151} ax_filtered //new filter2 detecting leg motion   → bad accuracy
			
			duplicate/O ax_filtered ax_var
			ax_var = 0
			
			j = 0
			do
				ax_var[j] = variance(ax_filtered,pnt2x(ax_filtered,j),pnt2x(ax_filtered,j+range))
				j += 1
			while(j<numpnts(ax_filtered)-range)
			
			j = 0
			variable temporary_top = 0
			
				//助走の終わりを探す
				do
					temporary_top = wavemax(ax_var,leftx(ax_var),pnt2x(ax_var,j))
					if(ax_var[j]<temporary_top/20)
						end_run = j
						break
					endif
					end_run = j
					j += 1
				while(j<numpnts(ax_var))
				
				
				variable first_peak = temporary_top

				//助走の開始を探す
				reverse_i = 1
				do
					if(ax_var[end_run - reverse_i]<first_peak/50)
						start_run = j - reverse_i
						break
					endif
					start_run = j - reverse_i
					reverse_i += 1
				while(j - reverse_i > 0)
			
			//助走時間を記録
			running_time = (end_run - start_run)/100

			if(running_time < 1 || 14 < running_time)
				appendvalue(running_time_list,Nan)
			else
				appendvalue(running_time_list,running_time)
			endif
			
			//助走マスクを作成
			running_mask_kari[x2pnt(running_mask_kari,pnt2x(ax_var,start_run)),x2pnt(running_mask_kari,pnt2x(ax_var,end_run))] = 1
			
		endif
		i += 1
	while(i<numpnts(TO_P))
	
   if(m == 0)
   		duplicate/O running_mask_kari running_mask_new
   elseif(m == 1)
   		duplicate/O running_mask_kari running_mask_new2
   endif
	
	endfor //Ninjaを2つ装着したワタリ用のループ終わり
	
	killwaves ax_filtered, ax_var, running_mask_kari, accel,TO_P
end



//飛び立ち後、羽ばたいた回数、10、30秒間の羽ばたき回数を検出
function flapping_num2()
	wave az, az2
	wave running_mask_new, running_mask_new2 
	
	make/O/N=0 flap_num10_list
	make/O/N=0 flap_num30_list
	
	variable runstart
	variable flap_counter = 0
	
	Variable i = 1
	variable j = 1
	variable m

	for(m=0; m<2; m+=1)  //Ninjaを2つ装着したワタリ用のループ
	 
	if(m == 0)
		duplicate/O az accel
		duplicate/O running_mask_new mask
		i = 1
	else
		if(waveexists(DPspd_avg2)==1)
			duplicate/O az2 accel
			duplicate/O running_mask_new2 mask
			i = 1
	 	else
	 		break
		endif
	endif

	do
		if(mask[i]-mask[i-1] == -1)
			flap_counter = 0
			j = 1
			variable kiritori_hajime = i 
			variable kiritori_owari  = i + 3000
			
			
			duplicate/O/R=[kiritori_hajime, kiritori_owari] accel az_filtered
			FilterFIR/DIM=0/LO={0.035,0.04,200}/HI={0.0125,0.0175,200} az_filtered
			
			do
				if(az_filtered[j-1] > -2 && az_filtered[j] < -2)
					flap_counter += 1
				endif
				
				if(j == 1000)
					appendvalue(flap_num10_list, flap_counter)
				endif
				
				j += 1
			while(j<3000)
			
			appendvalue(flap_num30_list, flap_counter)
			
		endif
		
		
		i += 1
	while(i<numpnts(mask))
	
	endfor //Ninjaを2つ装着したワタリ用のループ終わり
	
	killwaves  mask, accel, az_filtered
end


//風と波と飛び立ちデータをCSVで保存
function save_takeoff_CSV()
	string birdID
//	string filename = igorinfo(1) + "takeoff_new"+ ".csv"
	string filename = igorinfo(1) + "takeoff_new_15mw"+ ".csv"
	string datalist
	datalist  = "wind_spd_list;wind_dir_list;TO_dir_list2;sgh_list;sgp_list;sgd_list;AIC_list"
	datalist += ";running_time_list;s2down_mean_list;alt_delta_list;DPspd_delta_list;run_start_height_list"
	datalist += ";run_start_height_list2;run_start_height_list3_1;run_start_height_list3_2;run_start_height_list3_3"
	datalist += ";top_speed_list;top_speed_time_list;before_top_speed_list;before_top_speed_time_list"
	datalist += ";flap_num1_list;flap_num2_list;flap_stop_time1_list;flap_stop_time2_list;flap_num10_list;flap_num30_list"
	datalist += ";flap_freq_list5;cruis_dir_list;DPspd_list"
	Save/B/J/M="\r\n"/DLIM=","/W/F datalist as filename
end



