version 17
clear all
use "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\final_instrument\data\kedarnath_final_n200_full.dta"
log using "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\final_instrument\checks\show_labels.log", replace text
describe occupation employment_type inc_yatra_pm income_seasonality_cv tk_electric emp_dep_cond poor
notes tk_electric
notes emp_dep_cond
tabulate employment_type
tabulate tk_electric
list resp_id occupation employment_type inc_yatra_pm cons_pc_pm poor emp_dep_count tk_regular_n in 1/5, noobs
log close
