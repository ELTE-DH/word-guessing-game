#!/bin/bash

uniq_2nd_field="mawk -F\$'\t' -v OFS=\$'\t' '{ if (prev_field != \$1) {
                                                   prev_field=\$1;
                                                   for (i in count)
                                                       delete count[i];
                                                   count[\$2]++;
                                                   print \$0;
                                               } else {
                                                   count[\$2]++;
                                                   if (count[\$2] == 1)
                                                       print \$0;
                                               }
                                             }'"

eval $uniq_2nd_field
