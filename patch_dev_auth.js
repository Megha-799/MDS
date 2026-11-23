const fs = require('fs');

console.log('[Dev Auth Patch] Enabling Maker-Checker user switching & preview...');

// 1. Patch requireAuth to forward x-dev-user
const chunkFile = '.next/server/chunks/_4d8a4c53._.js';
if (fs.existsSync(chunkFile)) {
  let content = fs.readFileSync(chunkFile, 'utf8');
  // Handle both unpatched and previously patched
  if (content.includes('backendHeaders:{authorization:"Bearer dev-token"}')) {
    content = content.replace(
      'backendHeaders:{authorization:"Bearer dev-token"}',
      'backendHeaders:{authorization:"Bearer dev-token","x-dev-user":(e.cookies?.get("dev_user")?.value||"admin")}'
    );
    fs.writeFileSync(chunkFile, content, 'utf8');
    console.log('[Dev Auth Patch] Updated requireAuth in _4d8a4c53._.js to forward x-dev-user');
  } else if (content.includes(':r.NextResponse.json({errors:[{code:"G2P-AUT-LOGIN-REQUIRED",message:"Authentication required. No valid tokens found."}]},{status:401})')) {
    content = content.replace(
      ':r.NextResponse.json({errors:[{code:"G2P-AUT-LOGIN-REQUIRED",message:"Authentication required. No valid tokens found."}]},{status:401})',
      ':{accessToken:"dev-token",backendHeaders:{authorization:"Bearer dev-token","x-dev-user":(e.cookies?.get("dev_user")?.value||"admin")}}'
    );
    fs.writeFileSync(chunkFile, content, 'utf8');
    console.log('[Dev Auth Patch] Patched requireAuth in _4d8a4c53._.js');
  }
}

// 2. Patch /api/me to return Maker or Checker based on dev_user cookie
const meFile = '.next/server/chunks/[root-of-the-server]__5bbb2310._.js';
if (fs.existsSync(meFile)) {
  let content = fs.readFileSync(meFile, 'utf8');
  const replacementMe = 'async function y(e){let u=e.cookies?.get("dev_user")?.value;if(u==="checker"){return m.NextResponse.json({name:"Approver / Checker",preferred_username:"checker",sub:"checker-sub",email:"checker@moa.gov.et"})}return m.NextResponse.json({name:"Maker Officer (Admin)",preferred_username:"admin",sub:"admin-sub",email:"admin@moa.gov.et"})}';
  
  if (content.includes('async function y(e){return m.NextResponse.json({name:"Admin User",preferred_username:"admin",email:"admin@moa.gov.et"})}')) {
    content = content.replace('async function y(e){return m.NextResponse.json({name:"Admin User",preferred_username:"admin",email:"admin@moa.gov.et"})}', replacementMe);
    fs.writeFileSync(meFile, content, 'utf8');
    console.log('[Dev Auth Patch] Updated /api/me with Maker-Checker toggle');
  } else {
    const targetMe = 'async function y(e){let t=(0,E.requireAuth)(e);if(t instanceof m.NextResponse)return t;let r=(0,w.getBackendConfig)(),a=`${r.iamUrl}/auth/get_logged_in_user`,n=await fetch(a,{method:"GET",headers:t.backendHeaders,cache:"no-store"});return(0,C.jsonResponseFromBackend)(n)}';
    if (content.includes(targetMe)) {
      content = content.replace(targetMe, replacementMe);
      fs.writeFileSync(meFile, content, 'utf8');
      console.log('[Dev Auth Patch] Patched /api/me in __5bbb2310._.js');
    }
  }
}

// 3. Patch /api/permissions to include publish permissions
const permFile = '.next/server/chunks/[root-of-the-server]__ea885ac0._.js';
if (fs.existsSync(permFile)) {
  let content = fs.readFileSync(permFile, 'utf8');
  const replacementPerm = 'async function y(e){return g.NextResponse.json([{application_mnemonic:"master-data",permissions:["referenceData:view","referenceData:create","referenceData:edit","referenceData:delete","referenceData:publish","geo:view","geo:create","geo:edit","geo:delete","geo:publish"]}])}';
  
  if (content.includes('["referenceData:view","referenceData:create","referenceData:edit","referenceData:delete","geo:view","geo:create","geo:edit","geo:delete"]')) {
    content = content.replace(
      '["referenceData:view","referenceData:create","referenceData:edit","referenceData:delete","geo:view","geo:create","geo:edit","geo:delete"]',
      '["referenceData:view","referenceData:create","referenceData:edit","referenceData:delete","referenceData:publish","geo:view","geo:create","geo:edit","geo:delete","geo:publish"]'
    );
    fs.writeFileSync(permFile, content, 'utf8');
    console.log('[Dev Auth Patch] Updated /api/permissions with publish permissions');
  } else {
    const targetPerm = 'async function y(e){let t=(0,E.requireAuth)(e);if(t instanceof g.NextResponse)return t;let r=(0,w.getBackendConfig)(),a=`${r.iamUrl}/user-access/get_application_permissions_for_user?application_mnemonic=${r.applicationMnemonic}`,n=await fetch(a,{method:"GET",headers:t.backendHeaders,cache:"no-store"});return(0,C.jsonResponseFromBackend)(n)}';
    if (content.includes(targetPerm)) {
      content = content.replace(targetPerm, replacementPerm);
      fs.writeFileSync(permFile, content, 'utf8');
      console.log('[Dev Auth Patch] Patched /api/permissions in __ea885ac0._.js');
    }
  }
}

// 4. Patch /api/logout to toggle between Maker and Checker
const logoutFile = '.next/server/chunks/[root-of-the-server]__de2f786f._.js';
if (fs.existsSync(logoutFile)) {
  let content = fs.readFileSync(logoutFile, 'utf8');
  const targetLogout = 'async function w(){let e=(0,E.getBackendConfig)();return m.NextResponse.redirect(`${e.iamUrl}/auth/logout`)}';
  const replacementLogout = 'async function w(e){let u=e.cookies?.get("dev_user")?.value;let next=u==="checker"?"maker":"checker";let h=e.headers.get("host")||"localhost:3005";let p=e.headers.get("x-forwarded-proto")||"http";let res=m.NextResponse.redirect(new URL("/en",p+"://"+h));res.cookies.set("dev_user",next,{path:"/"});return res}';
  if (content.includes(targetLogout)) {
    content = content.replace(targetLogout, replacementLogout);
    fs.writeFileSync(logoutFile, content, 'utf8');
    console.log('[Dev Auth Patch] Patched /api/logout to toggle Maker / Checker');
  }
}

console.log('[Dev Auth Patch] Done!');
