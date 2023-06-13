create or replace procedure AddClient(new_name varchar2,new_address varchar2)
as begin
    insert into CLIENT(name, address) VALUES (new_name,new_address);
    commit;
end;

create or replace procedure AddItem(new_name varchar2,quantity int, price int)
as begin
    insert into Item(name, QUANTITY,PRICEPERDAY) VALUES (new_name,quantity,price);
    commit;
end;

create or replace type item_type as object(
    id int,
    name varchar2(100),
    quantity int,
    pricePerDay int
                                          );

create or replace type item_table is table of item_type;

create or replace type rented_item_type as object(
    id int,
    name varchar2(100),
    quantity int,
    pricePerDay int,
    rent_id int,
    date_from date,
    date_to date

                                          );
create or replace type rented_item_table is table of rented_item_type;

create or replace function AvailableItems(date_from date, date_to date) return item_table
as
    result item_table;
begin
    select item_type(id,name,QUANTITYOFAVAILABLEITEMS(id,date_from,date_to) ,pricePerDay) bulk collect
    into result
    from ITEM
    where QUANTITYOFAVAILABLEITEMS(id,date_from,date_to) > 0;
    return result;
end;

create or replace function MyReservations(client_id int) return rented_item_table
as
    result rented_item_table;
begin
    select rented_item_type(itemid,name,quantity,price,rentid,OUTDATE,DUEDATE) bulk collect
    into result
    from RENTEDITEMS
        where CLIENTID = client_id;
    return result;
end;



create or replace view RentedItems as
    select RENTID,ITEMID,name,price,CLIENTID,OUTDATE,DUEDATE,RENTITEMS.QUANTITY,STATUS from RENTITEMS
        join rent on RENTITEMS.RENTID = RENT.ID
        join item on item.id = RENTITEMS.ITEMID;



create or replace function QuantityOfAvailableItems(item_id int, date_from date, date_to date)
return int
as
    result int;
    my_quantity int;
begin
    select QUANTITY into my_quantity from ITEM where ID=item_id;

    select sum(QUANTITY)
    into result
    from RentedItems
        where ITEMID = item_id and not (date_from > RentedItems.DUEDATE or date_to < RentedItems.OUTDATE );
    if result is null then result := 0;
    end if;
    return (my_quantity - result);
end;

create or replace procedure AddRent(client_id int,date_from date,date_to date, my_status char)
as begin
    insert into RENT(clientid, outdate, duedate, status) values(client_id,date_from,date_to,my_status);
    commit;
end;

create or replace procedure AddItemToRent(rent_id int,item_id int,quantity int, my_price int)
as
    rent_exist int;
    item_exist int;
    date_from date;
    date_to date;
begin
    select count(*) into rent_exist from rent where id = rent_id;
    if rent_exist <=0 then raise_application_error(-20000,'nie ma takiego wypozyczenia');
        end if;

    select count(*) into item_exist from ITEM where item_id = id;
    if item_exist <=0 then raise_application_error(-20001,'nie ma takiego itemu');
    end if;

    select OUTDATE into date_from from RENT where rent_id = id;
    select DUEDATE into date_to from Rent where rent_id = id;

    if QuantityOfAvailableItems(item_id,date_from,date_to) < quantity then
        raise_application_error(-20002,'za malo dostepnych przedmiotow');
    end if;

    insert into RENTITEMS(rentid, itemid, quantity, price) VALUES (rent_id,item_id,quantity,my_price);
    commit;
end;


create or replace procedure MoveToHist(rent_id int, date_return date)
as
    client_id int;
    date_from date;
    date_to date;

begin
    select CLIENTID into client_id from RENT where rent_id = id;
    select OUTDATE into date_from from RENT where rent_id = id;
    select DUEDATE into date_to from RENT where rent_id = id;
    insert into RENTHIST(id, clientid, outdate, duedate, returndate) VALUES (rent_id,client_id,date_from,date_to,date_return);
    delete from RENT where id = rent_id;
end;

create or replace procedure ModifyStatus(rent_id int,new_status char)
as begin
    update RENT
        set STATUS = new_status
        where rent_id = id;
end;

create or replace type rent_type as object(
    id int,
    date_from date,
    date_to date
                                          );

create or replace  type rent_table is table of rent_type;


create or replace function ClientRents(client_id int) return rent_table
as
    result rent_table;
begin
    select rent_type(id,OUTDATE,DUEDATE) bulk collect
    into result
    from RENT
        where CLIENTID = client_id;
    return result;
end;


