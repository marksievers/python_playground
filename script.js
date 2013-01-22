var count = 1;
var users = db.user.find();

var rows = [];
var csv_columns = {'Id':'', 'Username':'', 'Name':'','Registered':'', 'Signed Up':'', 'Logged In':'', 'Parent Plans':'', 'Total Plans':'',
                   'Total Income($)':'', 'Total One Time Income($)':'', 'Total One Time Asset($)':'', 'Total Property($)':'',
                   'Total Recurring Expenses($)':'', 'Total One Time Expenses($)':'', 'Total Loans($)':''};

users.forEach(function(user) {
    row = {}
    person = db.person.findOne({"_id": user.person.$id});

    row['Id'] = person['_id'];
    row['Username'] = user.username;
    row['Name'] = user.name;
    row['Registered'] = 'N'

    if (user.signupDate) {
        row['Registered'] = 'Y'
        d = user.signupDate
        l = user.loginDate
        row['Signed Up'] = d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear();
        row['Logged In'] = l.getDate() + "/" + (l.getMonth() + 1) + "/" + l.getFullYear();
    }

    plans = person.plans;
    row['Total Plans'] = 0;
    row['Parent Plans'] = 0;
        
    for (i = 0; i < plans.length; i++) {
        plan = plans[i]
        
        route_plan(row, plan);
        add_value(row, 'Parent Plans', 1)
    }

    rows[count] = row;
    count++;

    //update column headers with dynamic fields
    for (key in row) {
        csv_columns[key] = ''
    }

    // print('\n')
    // print('User: ' + row['User'])
    // print('Parent Plans: ' + row['Parent Plans'])
    // print('Total Plans: ' + row['Total Plans'])

    // print('Plan types: ')
    // printjson(row['plan_type_count'])
    
    
    
    // print('Total Income($)' + row['Total Income($)'])
    // print('Total One Time Income($)' + row['Total One Time Income($)'])
    // print('Total One Time Asset($)' + row['Total One Time Asset($)'])

    // print('Total Property($)' + row['Total Property($)'])

    // print('Total Recurring Expenses($)' + row['Total Recurring Expenses($)'])
    // print('Total One Time Expenses($)' + row['Total One Time Expenses($)'])
    
    // print('Total Loans($)' + row['Total Loans($)'])
    
    // print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    // print('\n')
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

print(csv)

function trim_trailing_comma(str) {
    //trim last comma and newling
    last_comma_index = str.lastIndexOf(',')
    str = str.substring(0, last_comma_index)
    str += '\n' 

    return str
}

function route_plan(row, plan) {
    if (plan._class == 'com.planwise.domain.LoanPlan') {
        build_loan_plan(row, plan)         

    } else if (plan._class == 'com.planwise.domain.PropertyPlan') {
        build_property_plan(row, plan)

    } else if (plan._class == 'com.planwise.domain.GenericPlan') {
        build_generic_plan(row, plan)

    } else {
        //print('UNEXPECTED PLAN CLASS: ' + plan._class);
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

    //print('Property Plan')
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

    //print('Loan Plan')
    amount = parseInt(plan.principal)
    increment_plan_count(row, 'LOAN[' + plan.type + ']', amount);
    add_value(row, 'Total Loans($)', amount);
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
    
    //print('Generic Plan')
    //nested plans
    if (plan['plans'] && plan['plans'].length) {
        process_nested_plans(row, plan.plans)
    } else {
        process_cashflow(row, plan);
    }
}

function process_nested_plans(row, plans) {
    for (j = 0; j < plans.length; j++) {
        if (plans[j]['cashflow']) {
            process_cashflow(row, plans[j]);
            //print('  +' + plans[j].cashflow._class)
        } else {
            route_plan(row, plans[j]);
            //print('  ++' + plans[j]._class)
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
        //print('  *Recurring Exp');
        increment_plan_count(row, 'EXPENSE[' + plan.cashflow.expenseType + ']', amount);
        add_value(row, 'Total Recurring Expenses($)', amount);

    } else if (plan.cashflow._class == 'com.planwise.domain.SinglePaymentCashflow') {
        //print('  *Single Income/Payment');
        increment_plan_count(row, 'ONE TIME PAYMENT[' + plan.cashflow.type + ']', amount);
        
        if (plan.cashflow.type == 'INCOME') {
            add_value(row, 'Total One Time Income($)', amount);    
        } else if (plan.cashflow.type == 'ASSET') {
            add_value(row, 'Total One Time Asset($)', amount);    
        } else { //EXPENSE
            add_value(row, 'Total One Time Expenses($)', amount);    
        }

    } else if (plan.cashflow._class == 'com.planwise.domain.RegularIncomeCashflow') {
        //print('  *Regular Income');
        increment_plan_count(row, 'INCOME[' + plan.cashflow.incomeType + ']', amount);
        add_value(row, 'Total Income($)', amount);

    } else {
        //print("UNEXPECTED CASHFLOW")
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
