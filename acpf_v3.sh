#!/bin/bash


get_yang_data() {

cd $BASEDIR
echo "Running Yang script for ACPF" $(date +"%T")


cd $BASEDIR
split -d -l${split} $INPUTFILE batch_acpf_ --verbose

echo "Running Yang script for ACPF" $(date +"%T")
cd $BASEDIR
for i in $(ls batch_enb_*)
do
        cd $YANGDIR
        sh run_yang_v2.sh $BASEDIR/$i $CONFDIR/ACPF_cmd.xml $YANGOUTDIR &
        sleep 3
done
wait
echo all processes complete
}

parse_yang_data() {

PARSESCRIPT=/log/SEATools/tmpScripts/xml2csv.py

echo "Parsing ACPF XML Files" $(date +"%T")
#### PARSE PCRF XML ###

$PARSESCRIPT -c ${CONFDIR}/configured-gnb-ip-entries.conf -o ${TEMPDIR}/configured-gnb-ip-entries.csv ${YANGOUTDIR}/*.xml
$PARSESCRIPT -c ${CONFDIR}/configured-gnb-ip-address-entries.conf -o ${TEMPDIR}/configured-gnb-ip-address-entries.csv ${YANGOUTDIR}/*.xml
$PARSESCRIPT -c ${CONFDIR}/reserved-gnb-ip-entries.conf -o ${TEMPDIR}/reserved-gnb-ip-entries.csv ${YANGOUTDIR}/*.xml
$PARSESCRIPT -c ${CONFDIR}/reserved-gnb-ip-address-entries.conf -o ${TEMPDIR}/reserved-gnb-ip-address-entries.csv ${YANGOUTDIR}/*.xml

# Remove rows without actual ACPF data from csv file
grep -v ',,' ${TEMPDIR}/configured-gnb-ip-entries.csv > ${TEMPDIR}/non-blank-configured-gnb-ip-entries.csv
grep -v ',,,,,' ${TEMPDIR}/configured-gnb-ip-address-entries.csv > ${TEMPDIR}/non-blank-configured-gnb-ip-address-entries.csv
grep -v ',,' ${TEMPDIR}/reserved-gnb-ip-entries.csv > ${TEMPDIR}/non-blank-reserved-gnb-ip-entries.csv
grep -v ',,,,,' ${TEMPDIR}/reserved-gnb-ip-address-entries.csv > ${TEMPDIR}/non-blank-reserved-gnb-ip-address-entries.csv
}

create_report_reserved_gnb_ip(){
echo USM_ID,NE_ID,reserved-gnb-ip-index,usage-state,ip-index,interface-name,reserved-gnb-ipv4-address,reserved-gnb-ipv6-address,sw-version,RESULT > ${OUTPUTDIR}/$1
while IFS=, read -r USM_ID NE_ID reserved_gnb_ip_index usage_state ip_index interface_name reserved_gnb_ipv4_address reserved_gnb_ipv6_address sw_version
do
	if [ $USM_ID == "USM_ID" ]; then
		continue
	fi
	if [ -z "$reserved_gnb_ip_index" ]; then
		continue
	fi
	RESULT=PASS
	if [ -z "$usage_state" ] || [ -z "$ip_index" ] || [ -z "$interface_name" ] || [ -z "$reserved_gnb_ipv4_address" ] || [ -z "$reserved_gnb_ipv6_address" ] || [ -z "$sw_version" ]; then
		RESULT=FAIL
	fi
	echo "$USM_ID","$NE_ID","$reserved_gnb_ip_index","$usage_state ip_index","$interface_name","$reserved_gnb_ipv4_address","$reserved_gnb_ipv6_address","$sw_version","$RESULT" >> ${OUTPUTDIR}/$1
done < $TEMPDIR/reserved-gnb-ip.csv
}


create_report_configured_gnb_ip(){
echo USM_ID,NE_ID,configured-gnb-ip-index,gnb-id,ip-index,interface-name,configured-gnb-ipv4-address,configured-gnb-ipv6-address,sw-version,RESULT > ${OUTPUTDIR}/$1
while IFS=, read -r USM_ID NE_ID configured_gnb_ip_index gnb_id ip_index interface_name configured_gnb_ipv4_address configured_gnb_ipv6_address sw_version
do
	if [ $USM_ID == "USM_ID" ]; then
		continue
	fi
	if [ -z "$configured-gnb-ip-index" ]; then
		continue
	fi
	RESULT=PASS
	if [ -z "$gnb_id" ] || [ -z "$ip_index" ] || [ -z "$interface_name" ] || [ -z "$reserved_gnb_ipv4_address" ] || [ -z "$reserved_gnb_ipv6_address" ] || [ -z "$sw_version" ]; then
		RESULT=FAIL
	fi
	echo "$USM_ID","$NE_ID","$configured-gnb-ip-index","$gnb_id","$ip_index","$interface_name","$reserved_gnb_ipv4_address","$reserved_gnb_ipv6_address","$sw_version","$RESULT" >> ${OUTPUTDIR}/$1
done < $TEMPDIR/configured-gnb-ip.csv
}




############# MAIN ################

TMSTMP=`date -u +"%Y%m%d_%H%M%S_%Z"`

BASEDIR="/log/SEATools/ACPF_conf_resv/solution2"
CONFDIR="$BASEDIR/conf"
LOGSDIR="$BASEDIR/logs"
TEMPDIR="$LOGSDIR/temp"
OUTPUTDIR="$LOGSDIR/output"
YANGOUTDIR="$LOGSDIR/yangOutput"


YANGDIR="/log/SEATools/cli_tools/run_yang"
RESULTFILE="$OUTPUTDIR/output_${TMSTMP}.csv"


MKDIR_IFNOEX(){
  ls -d $1 >/dev/null 2>&1 || mkdir $1
}

MKDIR_IFNOEX $CONFDIR
MKDIR_IFNOEX $LOGSDIR
MKDIR_IFNOEX $OUTPUTDIR
MKDIR_IFNOEX $TEMPDIR
MKDIR_IFNOEX $YANGOUTDIR

if [[ $1 == "" ]]; then
        echo INPUT ARGUMENTS MISSING
        exit
elif [[ $1 == "ALL" ]]; then
        INPUTFILE="$YANGDIR/conf/sitelist/sitelist_acpf"
else
        INPUTFILE=$1
       
fi

\rm -f $YANGOUTDIR/*.xml
\rm -f $TEMPDIR/*.csv
\rm -f $TEMPDIR/*.lst

split=3000

get_yang_data $split

parse_yang_data

#create key file
create_key_file
#create_key_file reserved-gnb-ip

create_report_reserved_gnb_ip report_reserved_gnb_ip_${TMSTMP}.csv
create_report_configured_gnb_ip report_configured_gnb_ip_${TMSTMP}.csv