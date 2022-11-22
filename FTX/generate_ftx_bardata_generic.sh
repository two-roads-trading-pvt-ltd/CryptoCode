#!/bin/bash
#Main 
if [ $# -ne 3 ] ; then 
  echo "USAGE: YYYYMMDD/ALL PRODUCT[BTC] TRADE_FILE_DIR" ;  
  exit ;
fi 

for_date=$1
product=$2
trade_file_dir=$3
expiry_date_file="/NAS1/subham/FTXCryptoBarData/SCRIPT/expiry_date.txt"
bar_data_dir="/NAS1/subham/FTXCryptoBarData/BAR_DATA"
echo "OUTPUT_DIR: $bar_data_dir"

generate_bardata() {
    echo "$trade_file"
    file_date=`echo "$trade_file" | cut -d'_' -f3 | sed 's/-//g'`
    file_expiry=`echo "$trade_file" | cut -d'-' -f4 | cut -d'.' -f1`
    >/tmp/temp_expiry_crypto
    for expiry in `cat $expiry_date_file`; 
    do 
      [[ $expiry -ge $file_date ]] && echo "$expiry" >> /tmp/temp_expiry_crypto; 
    done;
    fut0_expiry=`sort /tmp/temp_expiry_crypto | head -1`
    fut1_expiry=`sort /tmp/temp_expiry_crypto | head -2 | tail -1`
    flag_fut=0
    [[ `echo $fut1_expiry | grep $file_expiry | wc -l` -eq 1 ]] && flag_fut=1;
    [[ $flag_fut -eq 0 ]] && symbol="${product}_FF_0_0" || symbol="${product}_FF_0_1" ;
    if [ $for_date == "ALL" ]; then
      [[ $flag_fut -eq 0 ]] && output_file="${bar_data_dir}/${product}_FUT0" || output_file="${bar_data_dir}/${product}_FUT1";
    else
      [[ $flag_fut -eq 0 ]] && output_file="${bar_data_dir}/${product}_FUT0_${for_date}" || output_file="${bar_data_dir}/${product}_FUT1_${for_date}";
    fi

    [[ $flag_fut -eq 0 ]] && expiry=$fut0_expiry || expiry=$fut1_expiry;
    

    start_=$(date -d "$file_date" +%s)
    low_="0"; high_="0"; open_="0"; close_="0"; open_time_="0"; close_time_="0"; volume_="0"; count_="0"; 
    for data in `zcat $trade_file`; do
      [[ `echo "$data" | cut -d',' -f1` == "exchange" ]] && continue;
      time_stamp=`echo "$data" | cut -d',' -f4`
      time_minute=`echo "${time_stamp:0:10}"`
      price=`echo "$data" | cut -d',' -f7`
      size=`echo "$data" | cut -d',' -f8`

      minute_=$((start_ + 60))
      while (( $(echo "$minute_ < $time_minute" | bc -l) ));
      do
          if(( $(echo "$open_ != 0" | bc -l) )); 
          then
                echo "$start_ $symbol $open_time_ $close_time_ $expiry $open_ $close_ $low_ $high_ $volume_ $count_" | awk '{printf"%d\t%s\t%d\t%d\t%d\t%f  %f  %f  %f  %f  %d\n", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11}' >> "$output_file"
                low_="0"; high_="0"; open_="0"; close_="0"; volume_="0"; count_="0"; 
          fi
          start_=$((start_ + 60))
          minute_=$((start_ + 60))
      done
      if(( $(echo "$open_ == 0" | bc -l) )); 
      then
          open_=$price
          close_=$price
          low_=$price
          high_=$price
          open_time_=${time_minute%.*}
          close_time_=${time_minute%.*}
          volume_=$size
          count_="1"
      else
          close_=$price
          close_time_=${time_minute%.*}
          volume_=$(echo "$volume_ + $size" | bc)
          count_=$((count_ + 1))
          if(( $(echo "$low_ > $price" | bc -l) )); 
          then
              low_=$price
          fi
          if(( $(echo "$high_ < $price" | bc -l) )); 
          then
              high_=$price
          fi
      fi
    done
    if(( $(echo "$open_ != 0" | bc -l) )); 
    then
        echo "$start_ $symbol $open_time_ $close_time_ $expiry $open_ $close_ $low_ $high_ $volume_ $count_" | awk '{printf"%d\t%s\t%d\t%d\t%d\t%f  %f  %f  %f  %f  %d\n", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11}' >> "$output_file"
    fi
}

cd $trade_file_dir
if [ $for_date == "ALL" ]; then
  for trade_file in `ls | grep "_${product}-" | grep -v "MOVE"`; do
    generate_bardata
  done
else
  grep_trade_file="${for_date:0:4}-${for_date:4:2}-${for_date:6:2}_${product}"  
  for trade_file in `ls | grep "$grep_trade_file" | grep -v "MOVE"`; do
    generate_bardata
  done
fi

