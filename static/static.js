'use strict';

document.querySelector('#date-filter > form > input[type="submit"]')
  .addEventListener('click', (evt) => {
    evt.preventDefault();

    const formInputs ={
        startDate: document.querySelector('#start-date').value,
        endDate: document.querySelector('#end-date').value,
    };

    fetch('/date', {
        method: 'POST',
        body: JSON.stringify(formInputs),
        headers:{
            'Content-Type': 'application/json',
        },
    })

        .then((response)=>response.json())
        .then((responseJson)=>{
          const profitMarginChartData = responseJson.profit_margin_chart_data.map(profitMargin => ({
            x: profitMargin.date, y: profitMargin.profit_margin
          }));

          const revenueChartData = responseJson.revenue_chart_data.map(revenue => ({
              x: revenue.date, y: revenue.revenue
            }));
          
          const expenseChartData = responseJson.expense_chart_data.map(expenses => ({
              x: expenses.date, y: expenses.expense
            }));

          new Chart(document.querySelector('#profit-margin-chart'), {
              type: 'line',
              data: {
                datasets: [{
                  label: 'Profit Margin',
                  data: profitMarginChartData,
                }],
              }});

          new Chart(document.querySelector('#revenue-expense-chart'), {
              type: 'bar',
              data: {
                datasets: [
                  {
                    label: 'Revenue',
                    data: revenueChartData,
                  },
                  {
                    label: 'Expenses',
                    data: expenseChartData,
                  },
                ],
              },
            });

            document.querySelector('#date-header').innerHTML = 
                `For ${responseJson.startDate} to ${responseJson.endDate}`;
            renderTable(responseJson);
        });
  });

  
function renderTable(responseJson) {
    document.querySelector('#net-sales').innerHTML = 
        responseJson.net_sales_per_class;
    document.querySelector('#expenses-per-class').innerHTML = 
        responseJson.expenses_per_class;
    document.querySelector('#payroll-per-class').innerHTML = 
        responseJson.payroll_per_class;
    document.querySelector('#total-discounts').innerHTML = 
        responseJson.discounts_percentage;
    document.querySelector('#profit-per-class').innerHTML = 
        responseJson.profit_per_class;
    document.querySelector('#profit-margin').innerHTML = 
        responseJson.profit_margin;
    document.querySelector('#occupancy-rate').innerHTML = 
        responseJson.occupancy_rate;
    document.querySelector('#average-bookings').innerHTML = 
        responseJson.average_bookings;
    document.querySelector('#break-even-bookings').innerHTML = 
        responseJson.break_even_bookings;
    document.querySelector('#net-sales-growth').innerHTML = 
        responseJson.MOM_sales_growth;
    document.querySelector('#expense-growth').innerHTML = 
        responseJson.MOM_expense_growth;
    document.querySelector('#new-students').innerHTML = 
        responseJson.new_students;
    document.querySelector('#retention').innerHTML = 
        responseJson.retention;
}
