def calculate_dial_interval(all_customers):
    first_customer = all_customers[0]
    last_customer = all_customers[-1]

    start_time = first_customer.ring_duration.start_time
    end_time = last_customer.ring_duration.end_time

    total_time = end_time - start_time

    average_dial_interval = total_time.total_seconds()/len(all_customers)

    return average_dial_interval