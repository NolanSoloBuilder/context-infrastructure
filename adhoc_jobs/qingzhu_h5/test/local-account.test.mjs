import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {handleAccount, initAccounts} from '../local/account.mjs';

function app() {
  const db = new DatabaseSync(':memory:');
  initAccounts(db);
  const call = async (method, path, body = {}, session = 'fixture-device') => {
    const res = {writeHead(status, headers) { this.status = status; this.headers = headers; },
      end(value) { this.data = Buffer.from(value); }};
    const sent = Symbol('sent');
    const data = await handleAccount({method}, res, new URL(path,'http://localhost'), {
      db, session, body: async () => body, sent,
      fail(code,message,status=200) { throw Object.assign(Error(message), {code,status}); }
    });
    return data === sent ? res : data;
  };
  return {db,call};
}

test('工具对设备直接免费开放，旧结算入口停用并保留本会话历史订单', async () => {
  const {db,call} = app();
  const login = await call('POST','/api/v1/users/login/device');
  assert.ok(login.token);
  assert.equal(login.user.is_local_device,true);
  assert.equal(login.user.is_vip,false);
  assert.equal(login.user.is_unlimited,true);
  const access = await call('GET','/api/v1/tools/unlock/status');
  assert.deepEqual(access.nickname,{unlocked:true,price:0,original_price:0});
  for (const [method,path] of [
    ['POST','/api/v1/payment/trial-vip/create'],
    ['POST','/api/v1/payment/alipay/prepay'],
    ['POST','/api/v1/payment/local-confirm'],
    ['GET','/api/v1/payment/local-checkout'],
    ['POST','/api/v1/coupons/1/claim'],
    ['POST','/api/v1/users/redeem'],
    ['POST','/api/v1/materials/create-order'],
    ['POST','/api/v1/tools/unlock/create-order'],
  ]) {
    await assert.rejects(call(method,path), error=>error.status===410, path);
  }
  assert.equal((await call('GET','/api/v1/orders')).total,0);
  db.prepare('INSERT INTO local_site_orders VALUES (?,?,?,?,?,?,?,?,?)').run(
    'legacy-1','fixture-device','trial_vip','历史记录',0,1,null,'2026-01-01','2026-01-01');
  assert.equal((await call('GET','/api/v1/orders')).total,1);
  const path='/api/v1/payment/order/legacy-1';
  assert.equal((await call('GET',path)).order_no,'legacy-1');
  await assert.rejects(call('GET',path,{},'another-device'), error=>error.status===404);
  db.close();
});

test('资料包内容真实，报告检索和下载限本机当前会话', async () => {
  const {call} = app();
  const materials = await call('GET','/api/v1/materials/list');
  assert.ok(materials.files.length>=3);
  const csvUrl = (await call('GET','/api/v1/materials/download/characters')).download_url;
  const csv = await call('GET',csvUrl);
  assert.match(csv.data.toString().split('\r\n')[0], /字符,拼音,五行/);
  const input = {surname:'林',name:'清妍',birth_date:'2020-01-01',birth_hour:'辰时',gender:'女'};
  const report = await call('POST','/api/v1/report/culture/create',input);
  const duplicate = await call('POST','/api/v1/report/culture/create',input);
  assert.equal(duplicate.report_id,report.report_id);
  assert.equal(report.status,'completed');
  const pdf = await call('GET',report.download_url);
  assert.equal(pdf.headers['Content-Type'],'application/pdf');
  assert.match(pdf.data.toString(),/^%PDF-1\.4/);
  assert.ok(pdf.data.toString().includes('/FontFile3') || pdf.data.toString().includes('/FontFile2'));
  await assert.rejects(call('GET',report.download_url,{},'another-device'),error=>error.status===404);
  assert.equal((await call('GET','/api/v1/report/my-reports')).length,1);
  assert.equal((await call('GET','/api/v1/report/my-reports',{},'another-device')).length,0);
});
