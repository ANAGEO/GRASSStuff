
#valeurs extrêmes pour le facteur d'échelle pour les cercles
export MAX=0.007
export MIN=0.001

for comcod in 63079
#for comcod in 85011 84077 84035 84033 52018 56001 52018 53065 62015 25031 25068 53084 55040 56016 25005 25037 54007 56049 52074
#for comcod in `psql xavier -Atq -c "select distinct on (cod_dom) cod_dom from data where cod_dom>25000 and cod_dom<26000;"`
#for comcod in `psql xavier -Atq -c "select distinct on (cod_dom) cod_dom from data where cod_dom>25000;"`
  do
   nomcom=`psql xavier -qAt -c "select nom from com where comcod=$comcod"`
   echo "En train de traiter $comcod: $nomcom"

   #d'abord les provenances
   psql xavier -q -c "drop view com_carto;"
   psql xavier -q -c "create view com_carto as select * from com left join (select cod_trav, revenus from data where cod_dom=$comcod and revenus>0) b on comcod=cod_trav"

   #calculer les valeurs pour la légende
   val1=`psql -Aqt -d xavier -c "select (trunc((max(revenus)/power(10,6))::numeric,1)*power(10,6)) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val1 where cat=1"
   val2=`psql -Aqt -d xavier -c "select trunc((((max(revenus)-avg(revenus))/2)/power(10,6))::numeric,1)*power(10,6) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val2 where cat=2"
   val3=`psql -Aqt -d xavier -c "select trunc((avg(revenus)/power(10,6))::numeric,1)*power(10,6) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val3 where cat=3"

   #calculer les valeurs à afficher dans la légende (en millions)
   leg1=`psql -Aqt -d xavier -c "select trunc((max(revenus)/power(10,6))::numeric,2) from com_carto where revenus>0"`
   leg2=`psql -Aqt -d xavier -c "select trunc((((max(revenus)-avg(revenus))/2)/power(10,6))::numeric,2) from com_carto where revenus>0"`
   leg3=`psql -Aqt -d xavier -c "select trunc((avg(revenus)/power(10,6))::numeric,2) from com_carto where revenus>0"`

   #calculer le facteur d'échelle pour la taille des cercles
    scale=`psql -Aqt -d xavier -c "SELECT CASE WHEN (select area from com_carto where comcod=$comcod)>8000 THEN (select trunc((area*0.003/sqrt(revenus))::numeric,5) from com_carto where comcod=$comcod) WHEN (select area from com_carto where comcod=$comcod) < 2000 THEN 0.003 WHEN (select revenus/sum from com_carto, (select sum(revenus) as sum from com_carto) b where comcod=$comcod) <0.25 THEN (select trunc((area*0.003/sqrt(revenus))::numeric,5) from com_carto where comcod=$comcod) ELSE (select trunc((area*0.004/sqrt(revenus))::numeric,5) from com_carto where comcod=$comcod) END;"`
    scale=`echo "if ($scale > $MAX) $MAX else $scale" | bc`
    scale=`echo "if ($scale < $MIN) $MIN else $scale" | bc`
    scale=0.001

    titre="Provenance des revenus nets du travail des habitants de $nomcom (2001)"
    #intégrer toutes les variables dans le fichier d'instructions de carto
    sed -e "s/LEG1/$leg1/" -e "s/LEG2/$leg2/" -e "s/LEG3/$leg3/" -e "s/TITRE/$titre/" -e "s/SCALE/$scale/" mod_carto_revenus.psmap > temp.psmap
    iconv -t ISO_8859-15 -f UTF-8 temp.psmap > temp.$comcod.psmap
    ps.map in=temp.$comcod.psmap out=CARTES/$comcod\_prov.ps --quiet
   # convert -size 480x640 CARTES/$comcod\_prov.ps CARTES/PNG/$comcod\_prov.png
    #rm temp.*psmap

   #et maintenant les destinations
   psql xavier -q -c "drop view com_carto;"
   psql xavier -q -c "create view com_carto as select * from com left join (select cod_dom, revenus from data where cod_trav=$comcod and revenus>0) b on comcod=cod_dom"

   #calculer les valeurs pour la légende
   val1=`psql -Aqt -d xavier -c "select (trunc((max(revenus)/power(10,6))::numeric,1)*power(10,6)) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val1 where cat=1"
   val2=`psql -Aqt -d xavier -c "select trunc((((max(revenus)-avg(revenus))/2)/power(10,6))::numeric,1)*power(10,6) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val2 where cat=2"
   val3=`psql -Aqt -d xavier -c "select trunc((avg(revenus)/power(10,6))::numeric,1)*power(10,6) from com_carto where revenus>0"`
   psql -q -d xavier -c "update belscale set valeur=$val3 where cat=3"

   #calculer les valeurs à afficher dans la légende (en millions)
   leg1=`psql -Aqt -d xavier -c "select trunc((max(revenus)/power(10,6))::numeric,2) from com_carto where revenus>0"`
   leg2=`psql -Aqt -d xavier -c "select trunc((((max(revenus)-avg(revenus))/2)/power(10,6))::numeric,2) from com_carto where revenus>0"`
   leg3=`psql -Aqt -d xavier -c "select trunc((avg(revenus)/power(10,6))::numeric,2) from com_carto where revenus>0"`

   #on utilise le même facteur d'échelle que pour les provenances, donc pas besoin de le recalculer

    titre="Destination des revenus nets du travail distribués à $nomcom (2001)"

    #intégrer toutes les variables dans le fichier d'instructions de carto
    sed -e "s/LEG1/$leg1/" -e "s/LEG2/$leg2/" -e "s/LEG3/$leg3/" -e "s/TITRE/$titre/" -e "s/SCALE/$scale/" mod_carto_revenus.psmap > temp.psmap
    iconv -t ISO_8859-15 -f UTF-8 temp.psmap > temp.$comcod.psmap
    ps.map in=temp.$comcod.psmap out=CARTES/$comcod\_dest.ps --quiet
   # convert -size 480x640 CARTES/$comcod\_dest.ps CARTES/PNG/$comcod\_dest.png
    #rm temp.*psmap
done
