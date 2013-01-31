/*
*@author Mark Sievers
*
*All users
*mongo planwise_db script.js > planwise.csv
* 
*Users from the last 7 days
*$mongo planwise_db --eval "var period='week'" script.js > planwise_week.csv
*
*/

//command line arg
var period;

var count = 1;
var users = db.user.find();

var rows = [];
var csv_columns = {'Id':'', 'Username':'', 'Name':'','Registered':'', 'Signed Up':'', 'Logged In':'', 'Parent Plans':'', 'Total Plans':'',
                   'Total Income($)':'', 'Total One Time Income($)':'', 'Total One Time Asset($)':'', 'Total Property($)':'',
                   'Total Recurring Expenses($)':'', 'Total One Time Expenses($)':'', 'Total Loans($)':'', 'Total Repayment($)':''};

var now = new Date()
var one_year = new Date()
one_year.setFullYear(now.getFullYear() + 1)

var milliseconds_in_day = 1000 * 60 * 60 * 24;

users.forEach(function(user) {
    row = {}
    person = db.person.findOne({"_id": user.person.$id});
    signup_date = user.signupDate

    if (period == 'week') {
        //process user from the last week
        if (signup_date && day_diff(signup_date, now) <= 7)  {
            process_entity(row, user, person)
        } 
    } else { //process all users
        process_entity(row, user, person)
    }
});


//create CSV line 1
csv = ''
count = 0;
for (key in csv_columns) {
    csv += key + ','
    count++;
}

csv = trim_trailing_comma(csv)

//loop through users
for (row in rows) {
    user = rows[row]
    
    //loop through csv col titles
    for (col in csv_columns) {
        if (user[col]) {
            csv += user[col] + ','
        } else {
            csv += ','
        }
    }
    
    csv = trim_trailing_comma(csv)
}

//out the final product
print(csv)

function process_entity(row, user, person) {
    row['Id'] = person['_id'];
    row['Username'] = user.username;
    row['Name'] = user.name;
    row['Registered'] = 'N'
    row['Parent Plans'] = 0;
    row['Total Plans'] = 0;

    signup_date = user.signupDate
    if (signup_date) {
        row['Registered'] = 'Y'
        d = signup_date
        l = user.loginDate
        row['Signed Up'] = d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear();
        row['Logged In'] = l.getDate() + "/" + (l.getMonth() + 1) + "/" + l.getFullYear();
    }

    plans = person.plans;
    for (i = 0; i < plans.length; i++) {
        plan = plans[i]
        
        route_plan(row, plan);
        process_future_plan(row, plan);
        add_value(row, 'Parent Plans', 1)
    }

    rows[count] = row;
    count++;

    //update column headers with dynamic fields
    for (key in row) {
        csv_columns[key] = ''
    }
}

function route_plan(row, plan) {
    if (plan._class == 'com.planwise.domain.LoanPlan') {
        build_loan_plan(row, plan)         

    } else if (plan._class == 'com.planwise.domain.PropertyPlan') {
        build_property_plan(row, plan)

    } else if (plan._class == 'com.planwise.domain.GenericPlan') {
        build_generic_plan(row, plan)
    }
}

/* Doesnt contribute to total plan count, just a metric on plans that are future type */
function process_future_plan(row, plan) {
    //return if this is not a future type plan
    if (!plan.viewName || plan.viewName.indexOf('future') == -1) { return }
        
    date = null
    
    //find an occurance of the future date for this plan (may have to dig into children to find it)
    if (plan.date) {
        date = plan.date
    } else if (plan.cashflow) {
        date = plan.cashflow.date
    } else {
        for (nested_plan in plan.plans) {
            if (plan.plans[nested_plan].cashflow) {
                date = plan.plans[nested_plan].cashflow.date
                break
            } else if (plan.plans[nested_plan].date) {
                date = plan.plans[nested_plan].date
                break
            }
        }
    } 
    
    //parse the type from the uri
    uri_tokens = plan.viewName.split('/')
    future_plan_type = uri_tokens[uri_tokens.length - 1]
    
    add_value(row, 'FUTURE[' + future_plan_type + ']', 1);
    
    if (date != null) {
        date = to_date(date);
        if (date < one_year) {
            add_value(row, 'FUTURE[' + future_plan_type + '](<12mnths)', 1);        
        }
    }
}

function build_property_plan(row, plan) {
    // _id
    // propertyValue
    // plans
    // name
    // viewName
    // active
    // _class
    // canceledRentExpensePlanId
    // cancelPaymentChangeId

    amount = parseInt(plan.propertyValue)
    increment_plan_count(row, 'PROPERTY', amount);
    add_value(row, 'Total Property($)', amount);

    if (plan['plans'] && plan['plans'].length) {
        process_nested_plans(row, plan.plans);
    }
}

function build_loan_plan(row, plan) {
    // _id
    // date
    // type [AUTO, STUDENT , CREDITCARD, PERSONAL] 
    // principal
    // annualInterestRate
    // monthlyAmount
    // loanChangeSet
    // amortizationMap
    // name
    // viewName
    // active
    // _class

    amount = parseInt(plan.principal)
    increment_plan_count(row, 'LOAN[' + plan.type + ']', amount);
    add_value(row, 'Total Loans($)', amount);

    total_repayments = 0
    if (plan.amortizationMap) {
        for (x in plan.amortizationMap) {
            payment = plan.amortizationMap[x]

            date = to_date(payment.date)
            if (date < now) {
                total_repayments = payment.balance
            }
        }
    }
    total_repayments =  parseInt(Math.abs(total_repayments))
    add_value(row, 'Total Repayment($)', total_repayments)
}

function build_generic_plan(row, plan) {
    // _id
    // cashflow
    // plans
    // name
    // active
    // _class
    // parentPlan
    // viewName
        // generic plan view names
        // -plans/current/income
        // -plans/current/spending
        // -plans/future/lumpsum
        // -plans/future/reducedebt
        // -plans/future/majorpurchase
        // -plans/future/buycar
        // -plans/future/spending    
    
    //nested plans
    if (plan['plans'] && plan['plans'].length) {
        process_nested_plans(row, plan.plans)
    } else if (plan.cashflow) {
        process_cashflow(row, plan);
    }
}

function process_nested_plans(row, plans) {
    for (j = 0; j < plans.length; j++) {
        if (plans[j]['cashflow']) {
            process_cashflow(row, plans[j]);
        } else {
            route_plan(row, plans[j]);
        }
    }
}

function process_cashflow(row, plan) {
    // cashflow.type [ASSET, EXPENSE, INCOME]

    // SinglePaymentCashflow
    // -type [ASSET, INCOME, EXPENSE]
    // -name
    // -amount
    // -date
    // -downpayment

    // RecurringExpenseCashflow
    // -type
    // -name
    // -amount
    // -date
    // -expensetype [OTHER]

    // RegularIncomeCashflow
    // -type [INCOME]
    // -name
    // -amount
    // -date
    // -incomeType [SALARY]

    amount = parseInt(plan.cashflow.amount)
    if (plan.cashflow._class == 'com.planwise.domain.RecurringExpenseCashflow') {
        increment_plan_count(row, 'EXPENSE[' + plan.cashflow.expenseType + ']', amount);
        add_value(row, 'Total Recurring Expenses($)', amount);

    } else if (plan.cashflow._class == 'com.planwise.domain.SinglePaymentCashflow') {
        increment_plan_count(row, 'ONE TIME PAYMENT[' + plan.cashflow.type + ']', amount);
        
        if (plan.cashflow.type == 'INCOME') {
            add_value(row, 'Total One Time Income($)', amount);    
        } else if (plan.cashflow.type == 'ASSET') {
            add_value(row, 'Total One Time Asset($)', amount);    
        } else { //EXPENSE
            add_value(row, 'Total One Time Expenses($)', amount);    
        }

    } else if (plan.cashflow._class == 'com.planwise.domain.RegularIncomeCashflow') {
        increment_plan_count(row, 'INCOME[' + plan.cashflow.incomeType + ']', amount);
        add_value(row, 'Total Income($)', amount);
    }
}

function increment_plan_count(row, type, value) {
    add_value(row, 'Total Plans', 1)
    add_value(row, type, 1)
    add_value(row, type + '$', value)
}

function add_value(row, key, value) {
    //aggregate value of key
    if (row[key]) {
        row[key] = row[key] + (value ? value : 1);

    } else {
        row[key] = value ? value : 1;
    }
}

function to_date(string) {
    tokens = string.split('-')
    
    date_num = parseInt(tokens[2], 10)
    date_month = parseInt(tokens[1], 10) - 1
    date_year = parseInt(tokens[0], 10)

    return new Date(date_year, date_month, date_num, 0, 0, 0, 0)
}

function month_diff(d1, d2) {
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth();
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}

function day_diff(d1, d2) {
    var delta_millis = d2.getTime() - d1.getTime();
    var days = delta_millis / milliseconds_in_day;
    return Math.floor(days);
}

function trim_trailing_comma(str) {
    //trim last comma and newline
    last_comma_index = str.lastIndexOf(',')
    str = str.substring(0, last_comma_index)
    str += '\n' 

    return str
}
