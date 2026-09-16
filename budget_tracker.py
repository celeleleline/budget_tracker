# budget tracker

# import things
import csv  # so u can read/write csv files for excel
import os  # so u cancheck if files exist
from datetime import datetime, timedelta  # todays date/time

# constants
TRANSACTIONS_FILE = "transactions.csv"
SETTINGS_FILE = "settings.csv"
DATE_FORMAT = "%Y-%m-%d"
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_WEEKLY_BUDGET = 100.00
DEFAULT_SAVINGS_GOAL = 200.00
TYPE_INCOME = "income"
TYPE_EXPENSE = "expense"

# classes
class Transaction:  # a single transaction (income/expense)

    def __init__(self, date, description, amount,
                 category, trans_type, tags=None):
        self.date = date  # runs this function when a new transaction is made
        self.description = description
        self.amount = amount
        self.category = category
        self.type = trans_type
        self.tags = tags if tags is not None else []  # if user doesnt give a tag, make an empty list
        self.created_at = datetime.now().strftime(DATE_FORMAT)  # automatic timestamp

    def __str__(self):  # string that shows when we print()
        return f"{self.date}: {self.description} - ${self.amount}"

    def is_expense(self):  # return true if expense, false if income
        return self.type == TYPE_EXPENSE

    def is_income(self):  # opposite to the 'is_expense' function
        return self.type == TYPE_INCOME

    def to_csv_row(self):  # convert to csv
        return [
            self.date,
            self.description,
            str(self.amount),
            self.category,
            self.type,
            ",".join(self.tags)
        ]


class Budget:  # main function, handles all budget related functions

    def __init__(self):  # runs at start, the main structure part
        self.trans: list[Transaction] = []  # main storage file
        self.cat: dict[str, dict] = {  # budget categories
            "food": {"budget": 50.00, "spent": 0.00},
            "transport": {"budget": 30.00, "spent": 0.00},
            "entertainment": {"budget": 40.00, "spent": 0.00},
            "school/study": {"budget": 25.00, "spent": 0.00},
            "shopping": {"budget": 30.00, "spent": 0.00},
            "savings": {"budget": 25.00, "spent": 0.00},
            "other": {"budget": 20.00, "spent": 0.00}
        }
        self.goals: dict[str, dict] = {}  # saving goals
        self.load_transactions()  # load data if it exists
        self.load_settings()

    def load_transactions(self):  # loads transactions from csv file
        if not os.path.exists(TRANSACTIONS_FILE):  # check if it exists
            return
        try:
            with open(TRANSACTIONS_FILE, 'r') as file:  # open and read the CSV file
                reader = csv.reader(file)
                next(reader)
                for row in reader:  # read each row and create a transaction
                    date = row[0]  # format is: date, description, amount, category, type, tags
                    description = row[1]
                    amount = float(row[2])
                    category = row[3]
                    trans_type = row[4]
                    tags = row[5].split(",") if len(row) > 5 and row[5] else []
                    transaction = Transaction(date, description, amount,
                                              category, trans_type, tags)  # creates an transaction 'object'
                    self.trans.append(transaction)  # add to the list
                    if trans_type == TYPE_EXPENSE and category in self.cat:  # update category spending total
                        self.cat[category]["spent"] += float(amount)
                    print(f"loaded: {transaction}")
            print(f"\nloaded {len(self.trans)} transactions!")
        except Exception as e:
            print(f"error loading transactions: {e}")
            print("creating new transaction file...")

    def save_transactions(self):  # save transactions whenever data is changed/added
        try:
            with open(TRANSACTIONS_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([  # write the header row
                    "date", "description", "amount", "category", "type", "tags"])
                for t in self.trans:  # write each transaction
                    writer.writerow(t.to_csv_row())
            print(f"saved {len(self.trans)} transactions!")
        except Exception as e:
            print(f"error saving transactions: {e}!")

    def load_settings(self):  # load budget settings
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[0] == "category_budget":  # format: category_budget, food, 50.00
                        category, budget = row[1], float(row[2])
                        if category in self.cat:
                            self.cat[category]["budget"] = budget
                    elif row[0] == "savings_goal":  # format: savings_goal, New Phone, 200.00, 50.00
                        goal_name, target, current = row[1], float(row[2]), float(row[3])
                        self.goals[goal_name] = {"target": target, "current": current}
        except Exception as e:
            print(f"error loading settings: {e}")

    def save_settings(self):  # save budget settings
        try:
            with open(SETTINGS_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["setting", "category/goal", "value", "extra"])
                for category, data in self.cat.items():  # save the category budgets
                    writer.writerow(["category_budget", category, f"{data['budget']:}", ""])
                for goal_name, data in self.goals.items():  # save the saving goals
                    writer.writerow(["savings_goal", goal_name,
                                     f"{data['target']:.}", f"{data['current']:}"])
            print("settings saved!")
        except Exception as e:
            print(f"error saving settings: {e}!")

    def add_transaction(self, date: str, description: str, amount: float,
                        category: str, trans_type: str,
                        tags: list[str] = None):  # manage transactions
        if not description or description.strip() == "":  # description cannot be empty, checks if its there
            return "error: description is required!"
        if amount <= 0:  # amount MUST be positive
            return "error: amount must be greater than $0!"
        if category not in self.cat:  # category must exist, checks it its there
            return f"error: category '{category}' not found!"
        try:  # date must be in the correct format, checks formatting
            datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            return f"error: date must be in format {DATE_FORMAT}!"
        transaction = Transaction(date, description, amount,
                                  category, trans_type, tags)  # creates the transaction object
        self.trans.append(transaction)  # adds it to the list
        if trans_type == TYPE_EXPENSE:  # updates the category spending, if expense
            self.cat[category]["spent"] += amount
        self.save_transactions()  # save to the file
        return f"added: {transaction}!"

    def get_transactions_by_date(self, date):  # gets transactions from a specific date
        results = []
        for t in self.trans:
            if t.date == date:
                results.append(t)
        return results

    def get_transactions_by_category(self, category):  # get transactions from a category
        results = []
        for t in self.trans:
            if t.category == category:
                results.append(t)
        return results

    def get_transactions_by_type(self, trans_type):  # gets transactions from a type
        results = []
        for t in self.trans:
            if t.type == trans_type:
                results.append(t)
        return results

    def search_transactions(self, term: str):  # gets trasnactions from description
        term = term.lower().strip()
        search_terms = term.split()
        results = []
        for t in self.trans:
            searchable = (t.description.lower() + " " + " ".join(t.tags).lower())
            matches = True
            for search_term in search_terms:
                if search_term not in searchable:
                    matches = False
                    break
            if matches:
                results.append(t)
        return results

    def get_all_transactions(self):  # return all transactions to display
        return self.trans

    def edit_transaction(self, index, date=None, description=None, amount=None,
                         category=None, trans_type=None, tags=None):  # edit transaction
        if index < 0 or index >= len(self.trans):  # check if index of transaction is valid
            return f"error: transaction not found (index {index})!"
        transaction = self.trans[index]
        original_desc = transaction.description
        if date is not None:  # updates the list
            try:  # validates the date format
                datetime.strptime(date, DATE_FORMAT)
                transaction.date = date
            except ValueError:
                return f"error: invalid date format, use {DATE_FORMAT}!"
        if description is not None:
            if not description or description.strip() == "":
                return "error: description cannot be empty!"
            transaction.description = description
        if amount is not None:
            if amount <= 0:
                return "error: amount must be greater than $0!"
            transaction.amount = amount
        if category is not None:
            if category not in self.cat:
                return f"error: category '{category}' not found!"
            transaction.category = category
        if trans_type is not None:
            if trans_type not in [TYPE_INCOME, TYPE_EXPENSE]:
                return f"error: type must be '{TYPE_INCOME}' or '{TYPE_EXPENSE}'!"
            transaction.type = trans_type
        if tags is not None:
            if tags:
                transaction.tags = [t.strip() for t in tags.split(',') if t.strip()]
            else:
                transaction.tags = []
        self.save_transactions()
        return f"updated transaction: {original_desc} → {transaction.description}!"

    def delete_transaction(self, index: int):  # deletes transaction by the index on list
        if index < 0 or index >= len(self.trans):  # checks if index is valid or not
            return f"error: transaction not found (index {index})!"
        transaction = self.trans[index]  # store the transaction for the message
        description, amount = transaction.description, transaction.amount
        removed = self.trans.pop(index)  # remove the transaction
        if removed.type == TYPE_EXPENSE and removed.category in self.cat:  # if it was an expense, update category spending
            self.cat[removed.category]["spent"] -= removed.amount
        self.save_transactions()  # save changes to file
        return f"deleted successfully!: {description} (${amount:})"

    def get_transaction_index(self, transaction: Transaction):  # finds the index for a transaction
        try:
            return self.trans.index(transaction)
        except ValueError:
            return -1

    def get_daily_summary(self, date: str = None):  # generate a saummary for a date
        if date is None:
            date = datetime.now().strftime(DATE_FORMAT)
        today_transactions = self.get_transactions_by_date(date)  # get transactions from today
        total_income = 0
        for t in today_transactions:  # calculate the totals
            if t.is_income():
                total_income += t.amount
        total_expenses = sum(t.amount for t in today_transactions if t.is_expense())
        net = total_income - total_expenses
        output = f"\ntodays finances! ({date})\n"  # format of the report
        output += "=" * 50 + "\n"
        output += f"income: ${total_income:}\n"
        output += f"expenses: ${total_expenses:}\n"
        output += f"net:${net:}\n"
        output += "-" * 50 + "\n"
        if today_transactions:
            output += "\ntransactions:\n"
            for t in today_transactions:
                output += f"  {t}\n"
        else:
            output += "no transactions recorded today.\n"
        return output

    def get_budget_progress(self):  # shows budget summary
        total_budget = 0
        total_spent = 0
        for category, data in self.cat.items():
            total_budget += data["budget"]
            total_spent += data["spent"]
        output = "\nbudget progress\n"
        output += "=" * 50 + "\n"
        output += f"total budget: ${total_budget:}\n"
        output += f"total spent: ${total_spent:}\n"
        # calc % of budget used
        if total_budget > 0:
            used_pct = (total_spent / total_budget) * 100
        else:
            used_pct = 0
        output += f"used: {used_pct:}%\n"
        if used_pct < 50:
            output += "😁 great job for staying under budget!"
        elif used_pct < 80:
            output += "☺️ good...but keep an eye on your spending..."
        else:
            output += "😐 getting close to budget limit there buddy..."
        return output

    def get_savings_progress(self):  # show progress
        if not self.goals:
            return "\nno savings goals set. add some!"
        output = "\nsavings goals\n"
        output += "=" * 50 + "\n"
        for goal_name, data in self.goals.items():
            current = data["current"]
            target = data["target"]
            pct = (current / target) * 100
            output += f"\n{goal_name}:\n"
            output += f"  ${current:.2f} / ${target:.2f} ({pct:.0f}%)\n"
            if pct < 30:
                output += "😁 keep saving!"
            elif pct < 70:
                output += "☺️ on track!"
            else:
                output += "😐 almost there!"
        return output

    def get_spending_analysis(self):  # analyze spending with a chart
        category_spending = {}  # spending by category
        for t in self.trans:
            if t.is_expense():
                category = t.category
                category_spending[category] = category_spending.get(category, 0) + t.amount
        if not category_spending:
            return "\nno spending data yet"
        # sort by the amount, highest first
        sorted_categories = []
        for category, amount in category_spending.items():
            sorted_categories.append((category, amount))
        for i in range(len(sorted_categories)):
            for j in range(i + 1, len(sorted_categories)):
                if sorted_categories[i][1] < sorted_categories[j][1]:
                    temp = sorted_categories[i]
                    sorted_categories[i] = sorted_categories[j]
                    sorted_categories[j] = temp

        total = sum(category_spending.values())
        output = "\nspending analysis\n"
        output += "=" * 50 + "\n"
        output += f"total spending: ${total:.2f}\n"
        output += "-" * 50 + "\n"
        for category, amount in sorted_categories:
            pct = (amount / total) * 100
            output += f"{category}: ${amount:.2f} ({pct:.0f}%)\n"
        if sorted_categories:  # find biggest spender
            top = sorted_categories[0]
            output += f"\n😱 most spent on: {top[0]} (${top[1]:.2f})"
        return output

    def get_weekly_report(self):  # weekly summary
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        week_ago_str = week_ago.strftime(DATE_FORMAT)  # convert to string to compare
        week_transactions = []  # get transactions from the last 7 days
        for t in self.trans:
            if t.date >= week_ago_str:
                week_transactions.append(t)

        total_income = sum(t.amount for t in week_transactions if t.is_income())
        total_expenses = sum(t.amount for t in week_transactions if t.is_expense())
        output = f"\nweekly report\n"
        output += "=" * 50 + "\n"
        output += f"period: {week_ago.strftime('%B %d')} - {today.strftime('%B %d')}\n"
        output += "-" * 50 + "\n"
        output += f"income: ${total_income:}\n"
        output += f"spent: ${total_expenses:}\n"
        output += f"net: ${total_income - total_expenses:}\n"
        output += "-" * 50 + "\n"
        output += f"total transactions: {len(week_transactions)}\n"
        output += f"average daily spend: ${total_expenses / 7:}\n"
        return output

# ui
def get_valid_date():  # asks for date
    while True:
        date_input = input("enter date (YYYY-MM-DD) or press enter for today!: "
        ).strip()
        if not date_input:
            return datetime.now().strftime(DATE_FORMAT)  # use today's date
        try:
            datetime.strptime(date_input, DATE_FORMAT)
            return date_input
        except ValueError:
            print(f"invalid date. use the correct format please: {DATE_FORMAT}")


# main program
def main():  # runs everything
    budget = Budget()  # creates budget manager
    print("\n" + "=" * 50)
    print("budget tracker!")
    print("=" * 50)
    print("  track your money spending & create saving goals!")
    print("=" * 50)
    while True:
        print("main menu")  # display menu
        print("-" * 50)
        print("1: add transaction")
        print("2: view todays summary")
        print("3: view budget summary")
        print("4: view savings goals")
        print("5: spending analysis")
        print("6: weekly report")
        print("7: search transactions")
        print("8: add savings goal")
        print("9: view all transactions")
        print("10: edit transaction")
        print("11: delete transactions")
        print("12: save & quit")
        print("-" * 50)
        choice = input("choose an option to run! (1-12): ").strip()  # get the users choice
        if choice == "1":
            print("\n" + "add transaction!")  # add transaction
            print("-" * 40)
            date = get_valid_date()
            description = input("description: ").strip()
            while True:  # validate the amount
                try:
                    amount = float(input("amount ($): "))
                    if amount <= 0:
                        print("amount must be positive!")
                        continue
                    break
                except ValueError:
                    print("please enter a valid number!")
            print("\ncategories:")  # show the categories
            for i, category in enumerate(budget.cat.keys(), 1):
                print(f"  {i}. {category}")
            while True:
                try:
                    category_num = int(input("choose category number: "))
                    categories = list(budget.cat.keys())
                    if 1 <= category_num <= len(categories):
                        category = categories[category_num - 1]
                        break
                    print(f"choose 1-{len(categories)}!")
                except ValueError:
                    print("please enter a real number!")
            print("\ntype:")  # type of transaction
            print("1: expense (money going out)")
            print("2: income (money coming in)")
            while True:
                try:
                    type_num = int(input("choose type: "))
                    if type_num == 1:
                        trans_type = TYPE_EXPENSE
                        break
                    elif type_num == 2:
                        trans_type = TYPE_INCOME
                        break
                    print("choose 1 or 2!")
                except ValueError:
                    print("please enter a real number!")
            tags_input = input("tags (comma separated, optional): ").strip()  # optional tags if u want
            tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
            result = budget.add_transaction(  # add the transaction
                date, description, amount,
                category, trans_type, tags
            )
            print(f"\n{result}")
        elif choice == "2":
            print(budget.get_daily_summary())  # get todays summary

        elif choice == "3":
            print(budget.get_budget_progress())  # get budget progress

        elif choice == "4":
            print(budget.get_savings_progress())  # get savings goals

        elif choice == "5":
            print(budget.get_spending_analysis())  # get analyze spending

        elif choice == "6":
            print(budget.get_weekly_report())  # get weekly report

        elif choice == "7":
            print("\nsearch transactions!")  # seach for transactions
            print("-" * 40)
            term = input("enter search term: ").strip()
            results = budget.search_transactions(term)
            if results:
                print(f"\nfound {len(results)} transactions for this term:")
                for t in results:
                    print(f"  {t}")
            else:
                print("no transactions found for this term")

        elif choice == "8":
            print("\nadd savings goal!")  # add savings goal
            print("-" * 40)
            goal_name = input("goal name (e.g., 'new ipad'): ").strip()
            if not goal_name:
                print("goal name required!")
                continue
            while True:
                try:
                    target = float(input("target amount ($): "))
                    if target <= 0:
                        print("target amount must be positive!")
                        continue
                    break
                except ValueError:
                    print("please enter a valid number!")
            while True:
                try:
                    current = float(input("current savings ($, default 0): ") or "0")
                    if current < 0:
                        print("current savings cannot be negative!")
                        continue
                    break
                except ValueError:
                    print("please enter a valid number!")
            budget.goals[goal_name] = {"target": target, "current": current}
            budget.save_settings()
            print(f"savings goal added: {goal_name}!")

        elif choice == "9":
            print("\nall transactions!")  # view all transactions
            print("-" * 40)
            transactions = budget.get_all_transactions()
            if not transactions:
                print("no transactions recorded yet 🥲")
                continue
            for i, transaction in enumerate(transactions, 1):  # show all transactions with numbers
                print(f"{i}.{transaction.date}: {transaction.description}")
                print(f"   amount: ${transaction.amount:} | category: {transaction.category}")
                if transaction.tags:
                    print(f"   tags: {', '.join(transaction.tags)}")
                print()

        elif choice == "10":
            print("\nedit transaction!")  # edit transaction
            print("-" * 40)
            transactions = budget.get_all_transactions()
            if not transactions:
                print("no transactions to edit 🥲")
                continue
            print("select a transaction to edit:")  # show all transactions with indexes
            for i, transaction in enumerate(transactions, 1):
                print(f"{i}. {transaction}")
            try:  # get selection of transactions
                selection = int(input("\nenter transaction number: "))
                if selection < 1 or selection > len(transactions):
                    print("invalid selection!")
                    continue
                index = selection - 1  # convert to 0-based index
                transaction = transactions[index]
                print(f"\nediting: {transaction}")
                print("\nwhat would you like to change?")
                print("1: date")
                print("2: description")
                print("3: amount")
                print("4: category")
                print("5: type (income/expense)")
                print("6: tags")
                print("7: cancel")
                field_choice = input("choose an option (1-7): ").strip()
                if field_choice == "1":
                    new_date = input("new date (YYYY-MM-DD) or enter for today: ").strip()
                    if not new_date:
                        new_date = datetime.now().strftime(DATE_FORMAT)
                    result = budget.edit_transaction(index, date=new_date)
                    print(result)
                elif field_choice == "2":
                    new_desc = input("new description: ").strip()
                    if not new_desc:
                        print("description cannot be empty!")
                        continue
                    print(budget.edit_transaction(index, description=new_desc))
                elif field_choice == "3":
                    try:
                        new_amount = float(input("new amount ($): "))
                        if new_amount <= 0:
                            print("amount must be positive!")
                            continue
                        print(budget.edit_transaction(index, amount=new_amount))
                    except ValueError:
                        print("please enter a valid number!")
                elif field_choice == "4":
                    print("\ncategories:")
                    for i, category in enumerate(budget.cat.keys(), 1):
                        print(f"  {i}. {category}")
                    try:
                        cat_num = int(input("choose category number: "))
                        categories = list(budget.cat.keys())
                        if 1 <= cat_num <= len(categories):
                            new_category = categories[cat_num - 1]
                            print(budget.edit_transaction(index, category=new_category))
                        else:
                            print("invalid category!")
                    except ValueError:
                        print("please enter a number!")
                elif field_choice == "5":
                    print("\ntype:")
                    print("1: expense")
                    print("2: income")
                    try:
                        type_num = int(input("choose type: "))
                        if type_num == 1:
                            print(budget.edit_transaction(index, type=TYPE_EXPENSE))
                        elif type_num == 2:
                            print(budget.edit_transaction(index, type=TYPE_INCOME))
                        else:
                            print("choose 1 or 2!")
                    except ValueError:
                        print("please enter a number!")
                elif field_choice == "6":
                    tags_input = input("new tags (comma separated): ").strip()
                    new_tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    print(budget.edit_transaction(index, tags=new_tags))
                elif field_choice == "7":
                    print("edit cancelled...")
                else:
                    print("invalid choice!")
            except ValueError:
                print("please enter a valid number!")

        elif choice == "11":
            print("\ndelete transaction")  # delete transaction
            print("-" * 40)
            transactions = budget.get_all_transactions()
            if not transactions:
                print("no transactions to delete 🥲")
                continue
            print("select a transaction to delete:")  # show all transactions with indexes
            for i, transaction in enumerate(transactions, 1):
                print(f"{i}. {transaction}")
            try:
                selection = int(input("\nenter transaction number (or 0 to cancel): "))
                if selection == 0:
                    print("delete cancelled!")
                    continue
                if selection < 1 or selection > len(transactions):
                    print("invalid selection!")
                    continue
                transaction = transactions[selection - 1]  # confirm deletion
                print(f"\nare you sure you want to delete:")
                print(f"   {transaction}")
                confirm = input("delete? y or n: ").strip().lower()
                if confirm == 'y' or confirm == 'yes':
                    index = selection - 1  # remove it
                    print(budget.delete_transaction(index))
                else:
                    print("delete cancelled!")
            except ValueError:
                print("please enter a valid number!")

        elif choice == "12":
            budget.save_transactions()  # save and quit program
            budget.save_settings()
            print("\nall data saved!")
            print("bye!")
            break
        else:
            print("invalid choice, please enter 1-12")


if __name__ == "__main__":  # the VERY beginning, runs when file is executed
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nprogram interrupted. bye!")
    except Exception as e:
        print(f"\nsorry an unexpected error occurred: {e}")
        print("please restart the program!")