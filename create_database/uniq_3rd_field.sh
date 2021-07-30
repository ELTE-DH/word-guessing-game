#!/bin/bash

uniq_3rd_field="mawk -F\$'\t' -v OFS=\$'\t' '{ if (prev_field != \$1) {
                                                   prev_field=\$1;
                                                   for (i in count)
                                                       delete count[i];
                                                   count[\$3]++;
                                                   print \$0;
                                               } else {
                                                   count[\$3]++;
                                                   if (count[\$3] == 1)
                                                       print \$0;
                                               }
                                             }'"

eval $uniq_3rd_field
