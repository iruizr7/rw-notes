package api

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/siyuan-note/siyuan/kernel/model"
	"github.com/siyuan-note/siyuan/kernel/util"
)

func TestAPIContractRWNotesLocalUser(t *testing.T) {
	previousConf, previousReadOnly := model.Conf, util.ReadOnly
	model.Conf, util.ReadOnly = model.NewAppConf(), true
	t.Cleanup(func() { model.Conf, util.ReadOnly = previousConf, previousReadOnly })
	for _, role := range []model.Role{model.RoleReader, model.RoleEditor, model.RoleAdministrator} {
		recorder := httptest.NewRecorder()
		context, _ := gin.CreateTestContext(recorder)
		context.Set(model.RoleContextKey, role)
		context.Request = httptest.NewRequest("POST", "/api/setting/getCloudUser", strings.NewReader(`{}`))
		getCloudUser(context)
		requireAPIContract(t, "POST", "/api/setting/getCloudUser", recorder)
		var result struct {
			Code int `json:"code"`
			Data *struct {
				UserID string `json:"userId"`
				Paid   int    `json:"userSiYuanOneTimePayStatus"`
			} `json:"data"`
		}
		if err := json.Unmarshal(recorder.Body.Bytes(), &result); err != nil {
			t.Fatal(err)
		}
		if result.Code != 0 {
			t.Fatalf("local user query failed: %s", recorder.Body.String())
		}
		if role == model.RoleAdministrator {
			if result.Data == nil || result.Data.UserID != "0" || result.Data.Paid != 1 {
				t.Fatalf("local entitlement response was lost: %s", recorder.Body.String())
			}
			if model.Conf.GetUser() == nil || model.Conf.UserData == "" {
				t.Fatal("local entitlement state was not retained")
			}
		} else if result.Data != nil || model.Conf.GetUser() != nil {
			t.Fatal("non-admin request disclosed or created local user state")
		}
	}
}
