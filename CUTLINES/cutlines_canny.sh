RASTMAP=ortho_2001_t792_1m
CANNY_LOWTHRES=1
CANNY_HITHRESH=5
CANNY_SIGMA=2
NUMBERLINES=20
EDGEWEIGHT=5
BORDERLINERESISTANCE=9999
OUTPUTRASTER=cutlines_canny
OUTPUTVECTORLINES=cutlines_canny
OUTPUTVECTORPOLYS=cutpolygons_canny
MINTILESIZE=40000
MEMORY=2000

echo "Identifying edges..."
eval $(g.region -g save=current --o)
i.edge $RASTMAP out=edge_tmp lthresh=$CANNY_LOWTHRES hthresh=$CANNY_HITHRESH sigma=$CANNY_SIGMA --o --q

echo "Calulating horizontal paths..."
NSSTEP=$(python -c "print 1.0*($n-$s-$nsres)/$NUMBERLINES")
python -c "for i in range(0,($NUMBERLINES+1)): print str($w+0.2*$ewres)+','+ str(($n-i*$NSSTEP)-$nsres/2.0)" > hstartpoints
python -c "for i in range(0,($NUMBERLINES+1)): print str($e-0.2*$ewres)+','+ str(($n-i*$NSSTEP)-$nsres/2.0)" > hstoppoints
v.in.ascii in=hstartpoints sep=comma out=hstart --o --q
v.in.ascii in=hstoppoints sep=comma out=hstop --o --q
v.distance from=hstart to=hstop out=hborderlines_tmp --o --q
HALFNSSTEP=$(python -c "print $NSSTEP / 2.0")
v.transform hborderlines_tmp yshift=-$HALFNSSTEP out=hborderlines --o --q
v.to.rast hborderlines use=val out=hborderlines type=line --o --q
r.mapcalc "hbase = if(isnull(hborderlines), if(edge_tmp==0, $EDGEWEIGHT, 1), $BORDERLINERESISTANCE)" --o --q
r.cost hbase startp=hstart stopp=hstop outp=hcumcost outdir=hdir memory=$MEMORY --o --q
r.drain -d in=hcumcost direction=hdir startp=hstop out=hlines --o --q

echo "Calulating vertical paths..."
EWSTEP=$(python -c "print 1.0*($e-$w-$ewres)/$NUMBERLINES")
python -c "for i in range(0,($NUMBERLINES+1)): print str(($e-i*$EWSTEP)-$ewres/2.0)+','+str($n-0.2*$nsres)" > vstartpoints
python -c "for i in range(0,($NUMBERLINES+1)): print str(($e-i*$EWSTEP)-$ewres/2.0)+','+str($s+0.2*$nsres)" > vstoppoints
v.in.ascii in=vstartpoints sep=comma out=vstart --o --q
v.in.ascii in=vstoppoints sep=comma out=vstop --o --q
v.distance from=vstart to=vstop out=vborderlines_tmp --o --q
HALFEWSTEP=$(python -c "print $EWSTEP / 2.0")
v.transform vborderlines_tmp xshift=+$HALFEWSTEP out=vborderlines --o --q
v.to.rast vborderlines use=val out=vborderlines type=line --o --q
r.mapcalc "vbase = if(isnull(vborderlines), if(edge_tmp==0, $EDGEWEIGHT, 1), $BORDERLINERESISTANCE)" --o --q
r.cost vbase startp=vstart stopp=vstop outp=vcumcost outdir=vdir memory=$MEMORY --o --q
r.drain -d in=vcumcost direction=vdir startp=vstop out=vlines --o --q

echo "Creating vector lines..."
r.patch hlines,vlines out=$OUTPUTRASTER --o --q
r.to.vect $OUTPUTRASTER out=$OUTPUTVECTORLINES type=line --o --q

echo "Creating vector polygons..."
g.region e=e-$ewres s=s+$nsres
v.in.region out=region type=line --o --q
g.region region=current
v.to.rast in=region out=region use=val type=line --o --q
r.patch $OUTPUTRASTER,region out=raster_polygons_tmp --o --q
r.thin raster_polygons_tmp out=raster_polygons --o --q
r.to.vect raster_polygons out=tmp1 type=line --o --q
v.category tmp1 op=del cat=-1 out=tmp2 --o --q
v.type tmp2 out=tmp3 --o --q
v.centroids tmp3 out=tmp4 --o --q
v.clean tmp4 tool=rmarea thresh=$MINTILESIZE out=$OUTPUTVECTORPOLYS --o --q

echo "Cleaning up..."
g.remove type=rast,vect name=base,hstart,vstart,hstop,vstop,hdrainstart,vdrainstart,hcumcost,vcumcost,hdir,vdir,hlines,vlines,edge_tmp,hbase,hborderlines,vbase,vborderlines,hborderlines_tmp,vborderlines,region,raster_polygons,raster_polygons_tmp,vborderlines_tmp,hborderlines,tmp1,tmp2,tmp3,tmp4,tmp_superp -f --q
rm hstartpoints hstoppoints vstartpoints vstoppoints


