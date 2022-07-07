from ..basic_role.customer import Customer


class CreateSomeCustomers():
    call_batch = 0

    def __init__(self):
        self.init_call_batch()

    @classmethod
    def init_call_batch(cls):
        cls.call_batch = 0

    @classmethod
    def create_some_customers(cls,
                              num_of_concurrent,
                              next_time_create_customer,
                              distribution_list,
                              prob_list,
                              manage_customers):

        '''
        产生多个客户客户
        args:
            start_customer_id:起始的客户id
            num_of_concurrent:产生的客户数量
            distribution_list:客户行为的概率分布
            prob_list:客户行为的概率分布2
            all_customers:
            manage_customers:
        '''
        cls.call_batch += 1
        for i in range(num_of_concurrent):

            new_customer = Customer.create_a_customer(distribution_list, prob_list, next_time_create_customer, cls.call_batch, random_seed=-1)

            # 更新manage_customers
            manage_customers.all_customers.append(new_customer)
            if hasattr(new_customer, 'success_transfer_to_artificial_seat'):
                manage_customers.occupy_seat_customers.append(new_customer)


