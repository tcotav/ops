import email, getpass, imaplib, datetime, re

# ref: http://stackoverflow.com/questions/7314942/python-imaplib-to-get-gmail-inbox-subjects-titles-and-sender-name?rq=1

user = raw_input("Enter your GMail username --> ")
gmailLabel="itunes"
NUM_DAYS=30

def process(str):
    lines=str.split("\r\n")
    orderNum=orderDate=orderTotal=0
    order={}
    orderItems=[]
    orderItem=None
    state=0
    pLine1=None
    pLine2=None
    linecount=0
    for l in lines:
        try: 
            linecount +=1
            if len(l) ==0: continue
            l=l.strip()
            if l[:4] == "----" and state==3: # closing ---------wall
                state=5
                break
            elif l[:9] == "Order Num":
                items=l.split(" ")
                order["id"] = items[2]
            elif l[:12] == "Receipt Date":
                items=l.split(" ")
                order["date"] = items[2]
            elif l[:11] == "Order Total":
                items=l.split(" ")
                order["total"] = items[2]
                # we know this is last item we want from email so exist loop
            elif l[:4] == "ype ":
                state=1
            elif l[:4] == "----" and state==1: # opening ---------wall
                state=2
            elif l[:4] == "----" and state==2: # opening. line 2 ---------wall
                state=3
            elif l[0] != '-' and (state==3):
                # first line of purchase
                pLine1=re.sub( '\s\s+', '|', l ).split('|')
                state=4
            elif l[0] != '-' and (state==4):
                pLine2=re.sub( '\s\s+', '|', l ).split('|')
                orderItems.append([pLine1[0].replace(","," "), pLine2[1]])
                state=3
        except:
            print "Error in line"
            print l
    order['items'] = orderItems
    return order

def getMail():
    # password prompt
    pwd = getpass.getpass("Enter your password --> ")

    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user, pwd)

    # select folder
    m.list()
    #m.select('inbox')
    m.select(gmailLabel)

    date = (datetime.date.today() - datetime.timedelta(NUM_DAYS)).strftime("%d-%b-%Y")
    (typ, data) = m.search(None, ('ALL'), '(SENTSINCE {0})'.format(date))
    ids = data[0]
    id_list = ids.split()
    #get the most recent email id
    latest_email_id = int( id_list[0] )

    msgDict={}
    for i in id_list:
        typ, data = m.fetch( i, '(RFC822)' )
        payload=""
        for response_part in data:
          if isinstance(response_part, tuple):
              msg = email.message_from_string(response_part[1])

              for part in msg.walk():
                  # multipart are just containers, so we skip them
                  if part.get_content_maintype() == 'multipart':
                    continue

                  # we are interested only in the simple text messages
                  if part.get_content_subtype() != 'plain':
                    continue
                  payload += part.get_payload()

        o=process(payload)
        msgDict[o["date"]] = o 

    keys=msgDict.keys()
    keys.sort(reverse=True)
    for k in keys:
        o=msgDict[k]
        print "%s,%s,,,%s" % (o['date'], o['id'], o['total'])
        for oi in o['items']:
            print ",,%s,%s" % (oi[0], oi[1])

if __name__ == "__main__":
    test=False

    if test:
        f=open("data.txt")
        s=""
        s=" ".join(f.readlines())
        o=process(s)
        print "DATE,ID,Item Name, Item Charge, TOTAL"
        print "%s,%s,%s" % (o['date'], o['id'], o['total'])
        for oi in o['items']:
            print ",%s,%s" % (oi[0], oi[1])
        f.close()

    getMail()
