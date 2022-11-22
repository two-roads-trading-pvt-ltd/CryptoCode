#!/bin/bash
#Main 
if [ $# -ne 3 ] ; then 
  echo "USAGE: bardata_fut0_file(unadjusted) bardata_fut1_file(unadjusted) PRODUCT[BTC]" ;  
  exit ;
fi 

bardata_file_fut0=$1
bardata_file_fut1=$2
product=$3
adjusted_output_file="/NAS1/subham/FTXCryptoBarData/ADJUSTED_BAR_DATA/${product}_FUT0"
echo "OUTPUT_FILE: $adjusted_output_file"

>${adjusted_output_file}
overall_count=0
while read -r start_ symbol open_time close_time expiry open close low high volume count
do
  [[ $overall_count -eq 0 ]] && expiry_date=$expiry;
  ((++overall_count))
  if [[ $expiry_date -eq $expiry ]]; then
    echo -e "$start_\t$symbol\t$open_time\t$close_time\t$expiry\t$open  $close  $low  $high  $volume  $count\t1" >> ${adjusted_output_file} 
    fut0_last_trade_time=$start_
    fut0_last_close_price=$close
  else
    fut1_last_close_price=`awk -v fut0_last_time=$fut0_last_trade_time '{if ($1 <= fut0_last_time) fut1_last_price=$7; next;} END {print fut1_last_price}' $bardata_file_fut1`
    echo "$fut0_last_trade_time $fut1_last_close_price $fut0_last_close_price"
    adj_factor=`echo | awk -v fut0_price=$fut0_last_close_price -v fut1_price=$fut1_last_close_price '{print fut1_price / fut0_price }'`
    echo "ratio $adj_factor $expiry_date $expiry"
    awk -v ratio=$adj_factor '{printf"%d\t%s\t%d\t%d\t%d\t%f  %f  %f  %f  %f  %d\t%f\n",$1,$2,$3,$4,$5,$6*ratio,$7*ratio,$8*ratio,$9*ratio,$10/ratio,$11,$12*ratio}' ${adjusted_output_file} > /tmp/temp_ftx_adjust_data

    mv /tmp/temp_ftx_adjust_data ${adjusted_output_file}
    next_working_day=`/home/pengine/prod/live_execs/update_date $expiry_date N A 1`
    next_day_timestamp=$(date -d "$next_working_day" +%s)
    awk -v fut0_last_time=$fut0_last_trade_time -v next_day_time=$next_day_timestamp '{if (($1 > fut0_last_time) && ($1 < next_day_time)) { printf"%d\t%s\t%d\t%d\t%d\t%f  %f  %f  %f  %f  %d\t1\n",$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11}}' $bardata_file_fut1 >> ${adjusted_output_file}
    echo -e "$start_\t$symbol\t$open_time\t$close_time\t$expiry\t$open  $close  $low  $high  $volume  $count\t1" >> ${adjusted_output_file}
    expiry_date=$expiry
  fi
done < ${bardata_file_fut0}

sed -i 's/_FF_0_1/_FF_0_0/g' ${adjusted_output_file}

