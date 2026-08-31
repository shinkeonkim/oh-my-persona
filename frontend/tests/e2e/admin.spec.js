import { expect, test } from '@playwright/test';
async function mockAdmin(page) {
  await page.addInitScript(() => sessionStorage.setItem('personaAdminToken', 'test-token'));
  await page.route('**/api/admin/**', async route => { const request=route.request(), path=new URL(request.url()).pathname; let body={};
    if(path==='/api/admin/knowledge') body={managed:[],packaged:[{id:'CHK-1',chunk_id:'CHK-1',document_id:'DOC-1',source_id:'SRC-1',title:'테스트 출처',content:'전체 청크 내용',source_path:'data/raw/test.md'}],packaged_total:1,packaged_unfiltered_total:1,source_facets:[]};
    else if(path==='/api/admin/chunks/CHK-1') body={id:'CHK-1',chunk_id:'CHK-1',document_id:'DOC-1',source_id:'SRC-1',title:'테스트 출처',content:'전체 청크 내용',source_path:'data/raw/test.md'};
    else if(path==='/api/admin/knowledge-gaps') body={questions:[{question_id:'PQ-1',question:'운영진 경험은 어땠나요?',category:'community',time_scope:'2024',status:'empty',unique_source_count:0,evidence_urls:[],answer_hint:'직접 답변하세요.'}]};
    else if(path==='/api/admin/conversations') body={conversations:[{id:'C-1',preview:'문의합니다',message_count:1,updated_at:'2026-08-31'}]};
    else if(path==='/api/admin/conversations/C-1') body={messages:[{role:'user',content:'문의합니다',sources:[]}]};
    else if(path.endsWith('/messages')) body={role:'owner',content:request.postDataJSON().content,sources:[]};
    await route.fulfill({status:path.endsWith('/messages')?201:200,contentType:'application/json',body:JSON.stringify(body)}); });
}
test('admin inspects chunks and knowledge gaps', async ({page}) => { await mockAdmin(page); await page.goto('/admin'); await page.getByRole('button',{name:/테스트 출처/}).click(); await expect(page.locator('.chunk-detail')).toContainText('전체 청크 내용'); await page.getByRole('button',{name:'지식 공백'}).click(); await expect(page.getByText('운영진 경험은 어땠나요?')).toBeVisible(); });
test('admin can intervene in a conversation', async ({page}) => { await mockAdmin(page); await page.goto('/admin'); await page.getByRole('button',{name:'대화 기록'}).click(); await page.getByRole('button',{name:/문의합니다/}).click(); await expect(page.getByPlaceholder('김신건으로 직접 답변')).toBeVisible(); });
