import{d as x,q as g,u as _,r as o,b,c as l,o as c,f as s,m as p,A as y,p as w,t as d,D as k,_ as R}from"./index-GEgtjqXc.js";import{i as B,c as C}from"./wechat-C5z14ogc.js";const A={class:"launch-page"},D={class:"card"},S={key:0,class:"code-line"},q={class:"code-val"},H={key:1,class:"hint"},L={key:2,class:"hint"},M={class:"hint-text"},N={key:3,class:"hint"},V=x({__name:"redeem-launch",setup(W){const h=g(),v=_(),t=o(""),i=o(null),r=o(!1),a=o(""),u=o(!1),m=()=>{v.replace({path:"/mine/redeem",query:t.value?{rcode:t.value}:{}})};return b(async()=>{if(t.value=h.query.rcode||"",u.value=B(),!!u.value)try{const{mpUsername:n}=await C();if(!n){a.value="小程序入口未配置";return}const e=i.value;if(!e){a.value="页面初始化失败";return}const f=t.value?`pages/mine-sub/redeem?rcode=${encodeURIComponent(t.value)}`:"pages/mine-sub/redeem";e.innerHTML=`
      <wx-open-launch-weapp
        username="${n}"
        path="${f}"
        style="display:block;width:100%;height:56px;"
      >
        <template>
          <style>
            .launch-btn {
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 8px;
              width: 100%;
              height: 56px;
              background: linear-gradient(135deg, #5B8C6A, #7BA98A);
              color: #fff;
              font-size: 17px;
              font-weight: 600;
              border-radius: 28px;
              border: none;
              box-shadow: 0 6px 16px rgba(91,140,106,0.25);
            }
            .launch-icon { font-size: 20px; }
          </style>
          <button class="launch-btn">
            <span class="launch-icon">🚀</span>
            <span>在小程序内一键兑换</span>
          </button>
        </template>
      </wx-open-launch-weapp>
    `,r.value=!0}catch(n){console.warn("[redeem-launch] JSSDK 配置失败:",n),a.value="加载失败，请刷新重试"}}),(n,e)=>(c(),l("div",A,[s("div",D,[e[3]||(e[3]=s("div",{class:"logo-wrap"},[s("span",{class:"logo-emoji"},"🎫")],-1)),e[4]||(e[4]=s("h1",{class:"title"},"青竹起名",-1)),e[5]||(e[5]=s("p",{class:"subtitle"},"在微信小程序内一键兑换",-1)),t.value?(c(),l("p",S,[e[0]||(e[0]=w("兑换码：",-1)),s("span",q,d(t.value),1)])):p("",!0),y(s("div",{ref_key:"launchRef",ref:i,class:"launch-slot"},null,512),[[k,r.value]]),u.value?a.value?(c(),l("div",L,[s("p",M,d(a.value),1),s("button",{class:"fallback-btn",onClick:m},"改用 H5 网页兑换")])):r.value?p("",!0):(c(),l("div",N,[...e[2]||(e[2]=[s("p",{class:"hint-text"},"正在加载小程序入口...",-1)])])):(c(),l("div",H,[...e[1]||(e[1]=[s("p",{class:"hint-text"},"请在微信中打开此链接",-1)])]))])]))}}),z=R(V,[["__scopeId","data-v-1dd27950"]]);export{z as default};
