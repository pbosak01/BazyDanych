create table item(
    id int generated always as identity not null,
    name varchar(100),
    quantity int,
    pricePerDay int,
    constraint item_pk primary key ( id ) enable
);

create table rent(
    id int generated always as identity not null,
    clientID int,
    outDate date,
    dueDate date,
    status char(1),
    constraint rent_pk primary key ( id ) enable
);


create table rentHist(
    id int not null ,
    clientID int,
    outDate date,
    dueDate date,
    returnDate date,
    constraint rentHist_pk primary key ( id ) enable
);

create table rentItems(
    rentId int,
    itemId int,
    quantity int
);

create table client(
    id int generated always as identity not null,
    name varchar(100),
    address varchar(100),
    constraint client_pk primary key (id) enable
);


alter table rentItems
add constraint  rentItems_fk1 foreign key
(itemId) references item (id) enable;

alter table rentItems
add constraint  rentItems_fk2 foreign key
(rentId) references rent (id) enable;

alter table rentItems
add constraint  rentItems_fk3 foreign key
(rentId) references rentHist (id) ;

alter table rent
add constraint  rent_fk2 foreign key
(clientId) references client (id) enable;

alter table rentHist
add constraint  rentHist_fk2 foreign key
(clientId) references client (id) enable;

alter table rentItems
add price int;

alter table rent
add constraint rent_chk1 check
(status in ('R','P','C')) enable;

