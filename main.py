import sqlite3
import sys
import random


def shopper_entry(db, cursor):
    query = '''SELECT shopper_first_name
               FROM shoppers
               WHERE shopper_id = ?
               '''

    shopper_id = input("Please enter your ID = ")
    cursor.execute(query, (shopper_id,))
    row = cursor.fetchone()

    if row:
        print("\n\x1b[0;36;40m" + f"Hello {row[0]}, welcome back to Orinocol" + "\x1b[0m\n")
        return shopper_id
    else:
        db.close()
        sys.exit("No customer found under that it, Goodbye")


def main():

    db = sqlite3.connect("Orinocol.db")
    cursor = db.cursor()

    shopper_id = shopper_entry(db, cursor)
    check_basket_on_runtime(cursor, db, shopper_id)
    delete_baskets_on_runtime(cursor, db)

    while True:
        print("\x1b[1;34;40m" + "ORINOCOL - SHOPPER MAIN MENU" + "\x1b[0m")
        print("\x1b[1;34;40m" + "______________________________________________________" + "\x1b[0m\n")
        print("1. Display your order history")
        print("2. Add an item to your basket")
        print("3. View your basket")
        print("4. Change the quantity of an item in your basket")
        print("5. Remove and item from your basket")
        print("6. Checkout")
        print("7. Exit\n")

        while True:
            try:
                menu_selection = int(input("User Input: "))
                if menu_selection not in (1, 2, 3, 4, 5, 6, 7):
                    print("Please make an appropriate selection")
                    continue
            except ValueError:
                print("Wrong Value, Please try again.")
            else:
                break

        if menu_selection == 1:
            order_history(cursor, shopper_id)
        elif menu_selection == 2:
            add_basket_item(db, cursor, shopper_id)
        elif menu_selection == 3:
            view_basket(cursor, shopper_id, change_basket=False)
        elif menu_selection == 4:
            change_quantity(db, cursor, shopper_id)
        elif menu_selection == 5:
            remove_item(db, cursor, shopper_id)
        elif menu_selection == 6:
            checkout_basket(cursor, db, shopper_id)
        elif menu_selection == 7:
            db.close()
            sys.exit("\nThank you for shopping with us!")


def order_history(cursor, shopper_id):
    query = ''' SELECT so.order_id, so.order_date, p.product_description, s.seller_name, op.price, op.quantity, op.ordered_product_status
                FROM ordered_products op
                JOIN product_sellers ps ON ps.seller_id = op.seller_id AND ps.product_id = op.product_id
                JOIN sellers s ON s.seller_id = ps.seller_id
                JOIN products p ON ps.product_id = p.product_id
                JOIN shopper_orders so ON so.order_id = op.order_id
                WHERE shopper_id = ?
                ORDER BY so.order_date DESC
                '''
    cursor.execute(query, (shopper_id,))
    results = cursor.fetchall()

    if results:
        print("\n{:7s}  {:8s}  {:80s} {:21s} {:9s} {:8s} {:8s}".format("OrderID", "Order Date", "Product Description",
                                                                       "Seller", "Price", "Qty", "Status"))
        previous_row = 0000000
        for row in results:
            if row[0] != previous_row:
                print("\n{:7d}  {:8s}  {:80s} {:20s}£ {:6.2f} {:5d}      {:8s}".format(row[0], row[1], row[2], row[3],
                                                                                       row[4], row[5], row[6]))
                previous_row = row[0]
            else:
                print(
                    "{:7s}  {:10s}  {:80s} {:20s}£ {:6.2f} {:5d}      {:8s}".format(" ", row[1], row[2], row[3], row[4],
                                                                                    row[5], row[6]))
        print("")
    else:
        print("No orders placed by this customer\n")


def view_basket(cursor, shopper_id, change_basket):
    query = ''' SELECT p.product_description, s.seller_name, bc.quantity, ps.price, bc.quantity*ps.price AS total
                FROM product_sellers ps LEFT OUTER JOIN basket_contents bc ON ps.seller_id = bc.seller_id AND ps.product_id = bc.product_id
                JOIN sellers s ON ps.seller_id = s.seller_id
                JOIN products p ON ps.product_id = p.product_id
                WHERE bc.basket_id = (  SELECT basket_id
                                        FROM shopper_baskets
                                        WHERE shopper_id = ?)
                ORDER BY total DESC
                '''
    cursor.execute(query, (shopper_id,))
    basket_rows = cursor.fetchall()
    total_sum = 0
    num_of_items = 0
    if basket_rows:
        print("Basket Contents")
        print("-----------------\n")
        print(
            "Basket Item  {:80s} {:32s} {:8s} {:8s}  {:6s}".format("Product Description", "Seller Name", "Qty", "Price",
                                                                   "Total"))
        for num, row in enumerate(basket_rows):
            print("      {:4d}   {:<80s} {:30s} {:^8d} £ {:6.2f}  £ {:6.2f}".format(num + 1, row[0], row[1], row[2],
                                                                                    row[3], row[4]))
            total_sum += row[4]
            num_of_items = num
        print("{:>106s} {:>38s} {:<5.2f}".format("Basket total", "£", total_sum))
        if change_basket:
            return basket_rows, num_of_items
    else:
        print("\nBasket is empty\n")
        return False, num_of_items


def add_basket_item(db, cursor, shopper_id):
    category_query = ''' SELECT category_description, category_id
                FROM categories'''
    cursor.execute(category_query)
    category_rows = cursor.fetchall()
    print("\nPlease choose an item category\n")
    cat_count = 0
    for num, id in enumerate(category_rows):
        print(f"{num + 1}. {id[0]}")
        cat_count = cat_count + 1

    while True:
        try:
            category_choice = int(input("\nUser input: "))
            if category_choice <= 0 or category_choice > cat_count:
                print(f"Selection not valid, please select an item between 1 and {cat_count}")
                continue
        except ValueError:
            print("Wrong Value")
        else:
            break

    print("\nProducts\n")
    product_query = ''' SELECT product_description, product_id
                        FROM products
                        WHERE category_id = ?
                        '''
    cursor.execute(product_query, (category_choice,))
    product_rows = cursor.fetchall()
    pro_count = 0
    for num, item in enumerate(product_rows):
        print(f"{num + 1}. {item[0]}")
        pro_count += 1

    while True:
        try:
            product_choice = int(input("\nUser input: "))
            if product_choice <= 0 or product_choice > pro_count:
                print(f"Selection not valid, please select an item between 1 and {pro_count}")
                continue
        except ValueError:
            print("Wrong Value")
        else:
            break

    product_id = product_rows[product_choice - 1][1]

    seller_query = '''  SELECT s.seller_name, ps.price, s.seller_id
                        FROM product_sellers ps JOIN sellers s ON s.seller_id = ps.seller_id
                        WHERE product_id = ?
                        '''
    cursor.execute(seller_query, (product_id,))
    seller_rows = cursor.fetchall()

    print("\nSellers who sell this product\n")
    sel_count = 0
    for num, item in enumerate(seller_rows):
        print("{}. {} (£{:.2f})".format(num + 1, item[0], item[1]))
        sel_count += 1

    while True:
        try:
            seller_choice = int(input("\nUser input: "))
            if seller_choice <= 0 or seller_choice > sel_count:
                print(f"Selection not valid, please select an item between 1 and {sel_count}")
                continue
        except ValueError:
            print("Wrong Value")
        else:
            break

    seller_id = seller_rows[seller_choice - 1][2]
    seller_price = seller_rows[seller_choice - 1][1]

    while True:
        try:
            item_qty = int(input("\nPlease enter item quantity: "))
            if item_qty == 0:
                print("Item quantity must be greater than 0")
                continue
            elif item_qty <= 0:
                print("Item quantity cannot be a negative integer")
                continue
        except ValueError:
            print("Please enter an integer")
        else:
            break

    shopper_basket_id_query = '''   SELECT basket_id
                                    FROM shopper_baskets
                                    WHERE shopper_id = ?'''

    cursor.execute(shopper_basket_id_query, (shopper_id,))
    basket_id_result = cursor.fetchone()
    basket_id = basket_id_result[0]

    add_basket_item_query = ''' INSERT INTO basket_contents(basket_id, product_id, seller_id, quantity, price)
                                VALUES (?, ?, ?, ?, ?)
                                '''
    cursor.execute(add_basket_item_query, (basket_id, product_id, seller_id, item_qty, seller_price))
    db.commit()


def change_quantity(db, cursor, shopper_id):
    basket_contents, num_of_items = view_basket(cursor, shopper_id, change_basket=True)
    if not basket_contents:
        return

    basket_len = len(basket_contents)
    if basket_len != 1:

        while True:
            try:
                item_selection = int(input("Please enter the basket item number for which you'd like to change quantity: "))
                if item_selection <= 0 or item_selection > basket_len:
                    print(f"Item no not found, please enter a value between 1 and {basket_len}")
                    continue
            except ValueError:
                print("Please enter an integer")
            else:
                break

        while True:
            try:
                quantity_selection = int(input("Please enter the new quantity you'd like to purchase: "))
                if quantity_selection == 0:
                    print("Quantity must be greater than zero")
                    continue
                elif quantity_selection <= 0:
                    print("Please enter a positive integer")
                    continue
            except ValueError:
                print("Please enter an integer")
            else:
                break

        obtain_product_id_query = '''   SELECT bc.product_id,bc.quantity*ps.price AS total
                                        FROM product_sellers ps LEFT OUTER JOIN basket_contents bc ON ps.seller_id = bc.seller_id AND ps.product_id = bc.product_id
                                        JOIN sellers s ON ps.seller_id = s.seller_id
                                        JOIN products p ON ps.product_id = p.product_id
                                        WHERE bc.basket_id = (  SELECT basket_id
                                                                FROM shopper_baskets
                                                                WHERE shopper_id = ?)
                                        ORDER BY total DESC'''
        cursor.execute(obtain_product_id_query, (shopper_id, ))
        product_id_result = cursor.fetchall()
        product_id = product_id_result[item_selection-1][0]

    else:
        while True:
            try:
                quantity_selection = int(input("Please enter the new quantity you'd like to purchase: "))
                if quantity_selection == 0:
                    print(f"Quantity must be greater than zero")
                    continue
                elif quantity_selection <= 0:
                    print("Please enter a positive integer")
                    continue
            except ValueError:
                print("Please enter an integer")
            else:
                break
        obtain_product_id_query = '''   select product_id 
                                                from basket_contents
                                                where basket_id = (select basket_id
                                                from shopper_baskets
                                                where shopper_id = ?)'''
        cursor.execute(obtain_product_id_query, (shopper_id,))
        product_id_result = cursor.fetchone()
        product_id = product_id_result[0]

    update_query = '''  update basket_contents 
                        set quantity = ?
                        where basket_id = ( select basket_id
                                            from shopper_baskets
                                            where shopper_id = ?)
                        and product_id = ?'''
    cursor.execute(update_query, (quantity_selection, shopper_id, product_id))
    db.commit()

    view_basket(cursor, shopper_id, change_basket=False)


def remove_item(db, cursor, shopper_id):
    basket_contents, num_of_items = view_basket(cursor, shopper_id, change_basket=True)
    if not basket_contents:
        return

    basket_len = len(basket_contents)
    if basket_len != 1:
        while True:
            try:
                item_selection = int(input("Please enter the basket item number for which you'd like to remove: "))
                if item_selection <= 0 or item_selection > basket_len:
                    print(f"Please enter a number between 1 and {basket_len}")
                    continue
            except ValueError:
                print("Please enter a valid selection")
            else:
                break

        obtain_product_id_query = '''   SELECT bc.product_id,bc.quantity*ps.price AS total
                                            FROM product_sellers ps LEFT OUTER JOIN basket_contents bc ON ps.seller_id = bc.seller_id AND ps.product_id = bc.product_id
                                            JOIN sellers s ON ps.seller_id = s.seller_id
                                            JOIN products p ON ps.product_id = p.product_id
                                            WHERE bc.basket_id = (  SELECT basket_id
                                                                    FROM shopper_baskets
                                                                    WHERE shopper_id = ?)
                                            ORDER BY total DESC'''
        cursor.execute(obtain_product_id_query, (shopper_id,))
        product_id_result = cursor.fetchall()
        product_id = product_id_result[item_selection - 1][0]

        while True:
            customer_sure = input("Are you sure you wish to delete this product (Y/N)? ")
            if customer_sure.upper() not in ("Y", "N"):
                print("Please enter an appropriate value")
            elif customer_sure.upper() == "N":
                print("Returning to main menu\n")
                return
            else:
                break

    else:
        while True:
            customer_sure = input("Are you sure you wish to delete this product (Y/N)? ")
            if customer_sure.upper() not in ("Y", "N"):
                print("Please enter an appropriate value")
            elif customer_sure.upper() == "N":
                print("Returning to main menu\n")
                return
            else:
                break

        obtain_product_id_query = '''   select product_id 
                                        from basket_contents
                                        where basket_id = (select basket_id
                                        from shopper_baskets
                                        where shopper_id = ?)'''
        cursor.execute(obtain_product_id_query, (shopper_id,))
        product_id_result = cursor.fetchone()
        product_id = product_id_result[0]

    delete_item_query = ''' delete from basket_contents
                            where basket_id = ( select basket_id
                                                from shopper_baskets
                                                where shopper_id = ?)
                            and product_id = ?'''

    cursor.execute(delete_item_query, (shopper_id, product_id))
    db.commit()

    view_basket(cursor, shopper_id, change_basket=False)


def checkout_basket(cursor, db, shopper_id):

    basket_value, num_of_items = view_basket(cursor, shopper_id, change_basket=True)

    if not basket_value:
        print("Your basket is empty, please add items in order to checkout\n")
        return

    while True:
        customer_sure = input("Do you wish to proceed with checkout (Y/N)? ")
        if customer_sure.upper() not in ("Y", "N"):
            print("Please enter an appropriate value")
        elif customer_sure.upper() == "N":
            print("Returning to main menu\n")
            return
        else:
            break

    get_basket_info = '''   select product_id, seller_id, quantity, price
                            from basket_contents
                            where basket_id = ( select basket_id from shopper_baskets
                                                where shopper_id = ?)'''
    cursor.execute(get_basket_info, (shopper_id,))
    basket_contents = cursor.fetchall()

    # generate order ID
    last_order_id_query = '''   select order_id from ordered_products
                                order by order_id desc'''
    cursor.execute(last_order_id_query)
    top_id = cursor.fetchone()
    new_id = top_id[0]
    new_id = new_id + random.randint(1, 50000)
    order_status = "Placed"

    generate_shopper_order = '''insert into shopper_orders
                                values(?, ?, date('now'), ?)'''
    cursor.execute(generate_shopper_order, (new_id, shopper_id, order_status))
    db.commit()

    for i in range(num_of_items + 1):
        generate_order_query = '''  insert into ordered_products
                                    values (?, ?, ?, ?, ?, ?)'''
        cursor.execute(generate_order_query, (new_id, basket_contents[i][0], basket_contents[i][1], basket_contents[i][2], basket_contents[i][3], order_status))
    db.commit()
    delete_baskets(cursor, db, shopper_id)

    create_todays_basket_query = '''INSERT INTO shopper_baskets (shopper_id, basket_created_date_time)
                                            VALUES (?, DATE('now'))
                                            '''
    cursor.execute(create_todays_basket_query, (shopper_id,))
    db.commit()

    print("\nCheckout complete, your order has been placed.\n")


def delete_baskets(cursor, db, shopper_id):

    delete_shopper_baskets = '''    delete from shopper_baskets where basket_id = (select basket_id from shopper_baskets
                                    where shopper_id = ?)'''
    delete_basket_contents = '''    delete from basket_contents where basket_id = (select basket_id from shopper_baskets
                                    where shopper_id = ?)'''
    cursor.execute(delete_basket_contents, (shopper_id,))
    cursor.execute(delete_shopper_baskets, (shopper_id,))
    db.commit()


def check_basket_on_runtime(cursor, db, shopper_id):
    check_todays_basket_query = ''' SELECT basket_id
                                    FROM shopper_baskets
                                    WHERE basket_created_date_time = DATE('now') AND shopper_id = ?'''
    cursor.execute(check_todays_basket_query, (shopper_id,))
    rows = cursor.fetchone()

    if not rows:
        create_todays_basket_query = '''INSERT INTO shopper_baskets (shopper_id, basket_created_date_time)
                                        VALUES (?, DATE('now'))
                                        '''
        cursor.execute(create_todays_basket_query, (shopper_id,))
        db.commit()


def delete_baskets_on_runtime(cursor, db):
    delete_basket_query = '''   DELETE FROM shopper_baskets WHERE basket_created_date_time <> DATE('now')'''
    cursor.execute(delete_basket_query)
    delete_basket_contents_query = '''  DELETE FROM basket_contents WHERE basket_id NOT IN (SELECT basket_id FROM shopper_baskets)'''
    cursor.execute(delete_basket_contents_query)
    db.commit()


if __name__ == "__main__":
    main()
