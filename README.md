# bluecoins-cli

> 🚧 **WARNING** 🚧
> 
> This sortware is at the very early stage of development. Use at your own risk and make sure to always have a database backup!

A CLI tool to manage the database of Bluecoins, an awesome budget planner for Android.

## Installation

You need GNU Make and Poetry installed. Run `make` to perform an entire CI pipeline - install dependencies, run linters and tests.

## Usage

1. Open the Bluecoins app. Go to *Settings -> Data Management -> Phone Storage -> Backup to phone storage*.
2. Transfer created `*.fydb` database backup file to the PC.
3. Run `bluecoins-cli mybackup.fydb convert` to convert a database to USD base currency.
4. Transfer created `mybackup.new.fydb` file to the smartphone. Go to *Settings -> Data Management -> Phone Storage -> Restore from phone storage*. Choose created file.

## Bluecoins database structure

`*.fydb` files generated by Bluecoins export are plain SQLite databases:

```text
➜  ~ file Bluecoins_2022-03-19_00_57_22.fydb 
Bluecoins_2022-03-19_00_57_22.fydb: SQLite 3.x database, user version 42, last written using SQLite version 3032002, file counter 11888, database pages 154, cookie 0x16, schema 4, largest root page 25, UTF-8, version-valid-for 11888
```

e.g., transactions are stored in `TRANSACTIONSTABLE` table. Columns we are interested in `convert` command scope are `transactionCurrency` and `conversionRateNew`.

```sql
SELECT transactionsTableID, conversionRateNew, transactionCurrency FROM TRANSACTIONSTABLE WHERE transactionCurrency != 'RUB' limit 5;
transactionsTableID  conversionRateNew   transactionCurrency
-------------------  ------------------  -------------------
1589351855443        0.0112947956665299  EUR                
1589351896182        0.0125486150829316  EUR                
1589352019668        0.011549686321133   EUR                
1589352314955        0.0125486150829316  EUR                
1589352314956        0.0125486150829316  EUR                
```

Another example, select all categories and their groups:

```sql
SELECT G.categoryGroupID, G.parentCategoryName, C.childCategoryName FROM CHILDCATEGORYTABLE C JOIN PARENTCATEGORYTABLE G ON C.parentCategoryID = G.parentCategoryTableID ORDER BY G.parentCategoryName, C.childCategoryName;
```
___

##  An archive command to move all account transactions to the virtual Archive account #6 

    
- Archive
    1. **Check**: acc_old_balance==0
        --where is Account balance? (check yourself)
    2. **Check**: account Archive exists. If not - create. 
        ```sql
        -- find account Archive
        SELECT * FROM ACCOUNTSTABLE
        WHERE ACCOUNTSTABLE.accountName='Archive';

        -- create account Archive
        insert into ACCOUNTSTABLE(accountName)
        values('Archive');
        --what can I do with other columns in the table?
        ```
    2. For all transaction: **add** labels #cli_archive and #cli_%name_acc_old%
        add label in LABELSTABLE with next last ID
        ```sql
        + labels : #cli_archive, #cli_%name_acc_old%

        -- find  all transactions Archive account:
        SELECT * FROM TRANSACTIONSTABLE
        WHERE TRANSACTIONSTABLE.accountID == ACCOUNTSTABLE.accountsTableID;        

        --add transactions in LABELSTABLE - rows
        INSERT INTO LABELSTABLE(labelName,transactionIDLabels)
        VALUES('cli_archive', /*TRANSACTIONSTABLE.transactionTableID*/);
        -- same with #cli_%name_acc_old%
        
        -- transactionIDLabels - ID transactions from TRANSACTIONSTABLE - transactionTableID
        ```

    4. Move transactions to Archive account. AccountID==id_acc_archive.
        ```sql
        --change accountID in transactions to Archive ID
        UPDATE TRANSACTIONSTABLE
        SET accountID = 1651056086581 --ID old account
        WHERE accountID == 1593593417685; --ID Archive account
        ```
    5. **Delete** acc_old.
        ```sql
        --delete old account
        select * from ACCOUNTSTABLE;
        where accountsTableID = 1593593417685; --ID old account
        ```

- Dearchive
    1. **Check**: account with name from tag #cli_%name_archive_account% exists. If not - create.


#### Hide from account selection and all reports

**App**
- transaction tab: hide in filter
- transaction tab: hide selected account transactions
- create transaction page: hide from account list
- main page: hide from reports

**BD**
- `TRANSACTIONSTABL` - no changes
- `ACCOUNTSTABLE` - accountHidden=1

#### Hide from account selection

**App**
- transaction tab: hide in filter
- create transaction page: hide from account list

**BD**
- `ACCOUNTSTABLE` - accountSelectorVisibility=1



*In backup keep the language preference interface.*
- `SETTINGSTABLE` - 2=%language%


*Tables:*
- `ACCOUNTSTABLE` - all created accounts;
- `ACCOUNTTYPETABLE` - static info

```text
format beautiful SQL tables
.headers on
.mode column

pragma table_info(?TABLE?); - view columns name
```
