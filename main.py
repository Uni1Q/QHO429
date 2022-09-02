import sqlite3
import sys


def shopper_entry(db, cursor):

    query = '''select shopper_first_name
               from shoppers
               where shopper_id = ?
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

        menu_selection = int(input("User Input: "))

        if menu_selection == 1:
            order_history(cursor, shopper_id)
        elif menu_selection == 2:
            add_basket_item(db, cursor, shopper_id)
        elif menu_selection == 3:
            view_basket(cursor, shopper_id)
        elif menu_selection == 4:
            pass
        elif menu_selection == 5:
            pass
        elif menu_selection == 6:
            pass
        elif menu_selection == 7:
            db.close()
            sys.exit("\nThank you for shopping with us!")


def order_history(cursor, shopper_id):

    query = ''' select so.order_id, so.order_date, p.product_description, s.seller_name, op.price, op.quantity, op.ordered_product_status
                from ordered_products op
                JOIN product_sellers ps ON ps.seller_id = op.seller_id AND ps.product_id = op.product_id
                JOIN sellers s ON s.seller_id = ps.seller_id
                join products p ON ps.product_id = p.product_id
                JOIN shopper_orders so ON so.order_id = op.order_id
                where shopper_id = ?
                order by so.order_date desc
                '''
    cursor.execute(query, (shopper_id, ))
    results = cursor.fetchall()

    if results:
        print("\n{:7s}  {:8s}  {:80s} {:21s} {:9s} {:8s} {:8s}".format("OrderID", "Order Date", "Product Description", "Seller", "Price", "Qty", "Status"))
        previous_row = 0000000
        for row in results:
            if row[0] != previous_row:
                print("\n{:7d}  {:8s}  {:80s} {:20s}£ {:6.2f} {:5d}      {:8s}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
                previous_row = row[0]
            else:
                print("{:7s}  {:10s}  {:80s} {:20s}£ {:6.2f} {:5d}      {:8s}".format(" ", row[1], row[2], row[3], row[4], row[5], row[6]))
    else:
        print("No orders placed by this customer")


def view_basket(cursor, shopper_id):

    query = ''' select p.product_description, s.seller_name, bc.quantity, ps.price, bc.quantity*ps.price as total
                from basket_contents bc join product_sellers ps ON bc.seller_id = ps.seller_id
                JOIN sellers s ON s.seller_id = ps.seller_id
                JOIN products p ON p.product_id = ps.product_id
                where bc.basket_id = (  select basket_id
                                        from shopper_baskets
                                        where shopper_id = ?)
                order by total desc
                '''
    cursor.execute(query, (shopper_id, ))
    basket_rows = cursor.fetchall()
    total_sum = 0
    if basket_rows:
        print("Basket Contents")
        print("-----------------")
        print("Basket Item  {:80s} {:32s} {:8s} {:8s}  {:6s}".format("Product Description", "Seller Name", "Qty", "Price", "Total"))
        for num, row in enumerate(basket_rows):
            print("      {:4d}   {:<80s} {:30s} {:^8d} £ {:6.2f}  £ {:6.2f}".format(num+1, row[0], row[1], row[2], row[3], row[4]))
            total_sum += row[4]
        print("{:>106s} {:>45}".format("Basket total", "£ " + str(total_sum)))
    else:
        print("Basket is empty")


def add_basket_item(db, cursor, shopper_id):

    category_query = ''' select category_description, category_id
                from categories'''
    cursor.execute(category_query)
    category_rows = cursor.fetchall()
    print("\nPlease choose an item category\n")
    for num, id in enumerate(category_rows):
        print(f"{num+1}. {id[0]}")
    category_choice = int(input("\nUser input: "))

    print("\nProducts\n")
    product_query = ''' select product_description, product_id
                        from products
                        where category_id = ?
                        '''
    cursor.execute(product_query, (category_choice, ))
    product_rows = cursor.fetchall()
    for num, item in enumerate(product_rows):
        print(f"{num+1}. {item[0]}")
    product_choice = int(input("\nUser input: "))
    product_id = product_rows[product_choice-1][1]

    seller_query = '''  select s.seller_name, ps.price, s.seller_id
                        from product_sellers ps JOIN sellers s ON s.seller_id = ps.seller_id
                        where product_id = ?
                        '''
    cursor.execute(seller_query, (product_id, ))
    seller_rows = cursor.fetchall()

    print("\nSellers who sell this product\n")
    for num, item in enumerate(seller_rows):
        print("{}. {} (£{:.2f})".format(num+1, item[0], item[1]))

    seller_choice = int(input("\nPlease enter choice of seller: "))
    seller_id = seller_rows[seller_choice-1][2]
    seller_price = seller_rows[seller_choice-1][1]
    item_qty = int(input("\nPlease enter item quantity: "))

    shopper_basket_id_query = '''   select basket_id
                                    from shopper_baskets
                                    where shopper_id = ?'''

    cursor.execute(shopper_basket_id_query, (shopper_id, ))
    basket_id_result = cursor.fetchone()
    basket_id = basket_id_result[0]

    add_basket_item_query = ''' insert into basket_contents(basket_id, product_id, seller_id, quantity, price)
                                values (?, ?, ?, ?, ?)
                                '''
    cursor.execute(add_basket_item_query, (basket_id, product_id, seller_id, item_qty, seller_price))
    db.commit()


def check_basket_on_runtime(cursor, db, shopper_id):

    check_todays_basket_query = ''' select basket_id
                                    from shopper_baskets
                                    where basket_created_date_time = date('now') and shopper_id = ?'''
    cursor.execute(check_todays_basket_query, (shopper_id, ))
    rows = cursor.fetchone()

    if not rows:
        create_todays_basket_query = '''insert into shopper_baskets (shopper_id, basket_created_date_time)
                                        values (?, date('now'))
                                        '''
        cursor.execute(create_todays_basket_query, (shopper_id, ))
        db.commit()


if __name__ == "__main__":
    main()
