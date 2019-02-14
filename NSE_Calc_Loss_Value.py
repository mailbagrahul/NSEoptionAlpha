def calculate_for_calls(chain_data):

    for current_index in range(0, len(chain_data)):

        current_strike = chain_data['Strike_Price'][current_index]

        # current_strike is a minimum of all strikes then no need to calculate the loss value for above strikes since all strikes are out of the money(OTM) i.e sellers are in profit side

        if current_strike == min(chain_data['Strike_Price']):
            hold_loss_value = 0
        else:
            hold_loss_value = 0
            for x in range(0, len(chain_data)):
                # if current strike less than equal to processing strike then sellers of particular strike is in profit so loss is zero
                if chain_data['Strike_Price'][x] >= current_strike:
                    hold_loss_value += 0
                else:
                    Diff_in_strike = current_strike - chain_data['Strike_Price'][x]
                    hold_loss_value = hold_loss_value + (Diff_in_strike * chain_data['CALLS_OI'][x])

        chain_data['Loss_Value_Of_Calls'][current_index] = hold_loss_value


def calculate_for_puts(chain_data):

    try:

        for current_index in range(0, len(chain_data)):

            current_strike = chain_data['Strike_Price'][current_index]

            # current_strike is a max of all strikes then no need to calculate the loss value for below strikes since all strikes are out of the money(OTM) i.e sellers are in profit side

            if current_strike == max(chain_data['Strike_Price']):
                hold_loss_value = 0
            else:
                hold_loss_value = 0
                for x in range(0, len(chain_data)):
                    # if current strike greater than equal to processing strike then sellers of particular strike is in profit so loss is zero
                    if chain_data['Strike_Price'][x] <= current_strike:
                        hold_loss_value += 0
                    else:
                        # chain_data['Strike_Price'][x] < current_strike:   --- only for PUTS
                        Diff_in_strike = chain_data['Strike_Price'][x] - current_strike
                        hold_loss_value = hold_loss_value + (Diff_in_strike * chain_data['PUTS_OI'][x])

            chain_data['Loss_Value_Of_Puts'][current_index] = hold_loss_value

    except KeyError:
        print("Error on Calculate_for_puts")
        return ""


def Calculate_Loss_Value(chain_data):
    print("****Calculate Loss Value****")

    # print(chain_data.shape)
    calculate_for_calls(chain_data)

    calculate_for_puts(chain_data)

    chain_data['Total_Loss'] = chain_data['Loss_Value_Of_Calls'] + chain_data['Loss_Value_Of_Puts']

    return chain_data
