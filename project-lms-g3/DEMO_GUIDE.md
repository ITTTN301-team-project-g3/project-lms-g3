# HUONG DAN DEMO LMS - STUDENTHUB

## 1. Tai khoan demo

Script `seed_data.py` tao/bo sung 3 tai khoan:

| Ho ten | Email | Mat khau |
|---|---|---|
| Nguyen Van An | demo1@lms.com | Demo@123456 |
| Tran Thi Binh | demo2@lms.com | Demo@123456 |
| Le Minh Khoa | demo3@lms.com | Demo@123456 |

Moi tai khoan co 8 mon hoc va 40 bai tap mau. Script co the chay lai; cac tai khoan, mon hoc va bai tap da co se duoc bo qua, khong tao trung.

## 2. Danh sach luong demo

### Luong 1 - Dang ky tai khoan moi
1. Mo `http://127.0.0.1:8000/static/register.html`.
2. Nhap ho ten, email chua ton tai va mat khau tu 6 ky tu.
3. Bam Dang ky.
4. He thong tao tai khoan, bam chuyen sang trang Dang nhap.
5. Thu dang ky lai email vua dung de minh hoa kiem tra email trung.

Ket qua mong doi: dang ky hop le tra ve thong bao thanh cong; email trung bi tu choi.

### Luong 2 - Dang nhap va xac thuc
1. Mo trang Dang nhap.
2. Dang nhap bang mot tai khoan demo.
3. He thong gui email/mat khau den API `/auth/login`.
4. JWT duoc luu trong `localStorage` voi key `access_token`.
5. Trinh duyet chuyen den Dashboard.

Ket qua mong doi: trang duoc bao ve; neu chua dang nhap hoac token het han thi quay ve trang Dang nhap.

### Luong 3 - Quan ly mon hoc
1. Tu Dashboard bam `Quan ly mon hoc`.
2. Xem danh sach mon hoc cua tai khoan hien tai.
3. Tao mon hoc moi voi ma mon, ten mon va mo ta.
4. Sua ten/ma/mo ta mon hoc.
5. Thu tao ma mon da ton tai de xem thong bao trung.
6. Thu xoa mon hoc co bai tap de minh hoa rang he thong khong cho xoa mon dang co bai tap.
7. Xoa mot mon hoc khong co bai tap neu can.

Ket qua mong doi: CRUD mon hoc hoat dong; du lieu duoc loc theo tai khoan.

### Luong 4 - Quan ly bai tap
1. Tu Dashboard bam `Quan ly bai tap`.
2. Xem danh sach bai tap mau.
3. Loc theo mon hoc hoac trang thai TODO / IN_PROGRESS / DONE.
4. Tao bai tap, chon mon hoc, han nop va trang thai.
5. Sua tieu de, mo ta, mon hoc, han nop hoac trang thai.
6. Xoa mot bai tap.

Ket qua mong doi: CRUD bai tap hoat dong; bai tap chi gan voi mon hoc cua tai khoan dang dang nhap.

### Luong 5 - Dashboard va canh bao han nop
1. Quay lai Dashboard.
2. Xem tong so mon hoc, tong bai tap, so bai dang lam va so bai da hoan thanh.
3. Khu vuc `Bai tap qua han` hien cac bai chua hoan thanh co han nop truoc thoi diem hien tai.
4. Khu vuc `Sap den han trong 7 ngay` hien cac bai chua hoan thanh co han nop trong 7 ngay toi.
5. Danh dau mot bai sap den han la DONE trong trang Quan ly bai tap, quay lai Dashboard va kiem tra bai do khong con nam trong danh sach canh bao.

Ket qua mong doi: so lieu Dashboard duoc tinh tu du lieu that trong database, khong phai so lieu viet cung trong HTML.

### Luong 6 - Kiem tra phan tach du lieu
1. Dang nhap `demo1@lms.com`, ghi nho danh sach mon hoc.
2. Dang xuat va dang nhap `demo2@lms.com`.
3. Kiem tra danh sach mon hoc/bai tap.
4. Tao mot mon hoc rieng tren tai khoan demo2.
5. Dang nhap lai demo1 va xac nhan khong thay mon hoc vua tao.

Ket qua mong doi: API chi tra ve du lieu cua tai khoan dang xac thuc.

## 3. Du lieu mau duoc tao

- 3 tai khoan demo.
- 8 mon hoc moi moi tai khoan (24 mon hoc neu database chua co).
- 5 bai tap moi moi mon (120 bai tap neu database chua co).
- Trang thai gom TODO, IN_PROGRESS va DONE.
- Han nop gom bai qua han, den han hom nay va bai sap den han.
