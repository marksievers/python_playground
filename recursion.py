def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

def get_start_issue_in_renewal_chain(subscription):
    if not subscription.renewal_of:
        return subscription.start_issue
    else:
        return get_start_issue_in_renewal_chain(subscription.renewal_of)



def get_start_issue_in_renewal_chain(self, subscription=None):
    if subscription:
        return self.get_start_issue_in_renewal_chain(subscription=self)
    else:
        if not subscription.renewal_of:
            return subscription.start_issue
        else:
            return self.get_start_issue_in_renewal_chain(subscription.renewal_of)