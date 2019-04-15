//var GPSceneUI = UIBase.extend({
var GPSceneUI = BasicDialogUI.extend({
    ctor:function() {
        this._super();
        this.resourceFilename = "res/ui/GPSceneUI.json";
        this.setLocalZOrder(const_val.GameConfigZOrder);
    },

    initUI:function(){
        var player = h1global.player();
        var self = this;
        var playerInfoList = player.curGameRoom.playerInfoList;
        cc.log(playerInfoList);

        this.gps_panel = this.rootUINode.getChildByName("gps_panel");
        this.Avatar_panel=this.gps_panel.getChildByName("Avatar_panel");
        this.word_panel=this.gps_panel.getChildByName("word_panel");


        for(var i = 0 ; i < playerInfoList.length ; i++){
            let idx = i;
            if(playerInfoList[i]==null){
                continue;
            }
            cutil.loadPortraitTexture(playerInfoList[i]["head_icon"], playerInfoList[i]["sex"], function(img){
                var portrait_sprite  = new cc.Sprite(img);
                portrait_sprite.setScale(100/portrait_sprite.getContentSize().width);
                var head_frame = self.Avatar_panel.getChildByName("head_frame_img_"+ idx.toString());
                head_frame.getChildByName("alert_img").setVisible(false);
                if(head_frame.getChildByName("portrait_sprite")){
                    head_frame.getChildByName("portrait_sprite").removeFromParent();
                }
                portrait_sprite.setName("portrait_sprite");
                head_frame.addChild(portrait_sprite);
                portrait_sprite.x+=69;
                portrait_sprite.y+=67;
            });
        }

        var distance = this.get_distance(2,3);
        this.word_panel.getChildByName("word_label_0").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
        var distance = this.get_distance(1,3);
        this.word_panel.getChildByName("word_label_1").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
        var distance = this.get_distance(0,3);
        this.word_panel.getChildByName("word_label_2").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
        var distance = this.get_distance(0,2);
        this.word_panel.getChildByName("word_label_3").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
        var distance = this.get_distance(0,1);
        this.word_panel.getChildByName("word_label_4").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
        var distance = this.get_distance(1,2);
        this.word_panel.getChildByName("word_label_5").setString(distance !== -1 ? (distance > 1000 ? parseInt(distance / 1000) + "k" : distance) + "m" : "距离未知");
    },

    get_distance:function (serverSitNum1,serverSitNum2){
        var player = h1global.player();
        //cc.log(player.curGameRoom.playerDistanceList);
        //var playerDistanceList = [[-1,200,300,199999], [200,-1,250,199999], [300,250,-1,199999], [199999,199999,1999999,-1]];
        var playerDistanceList = player.curGameRoom.playerDistanceList;
        var distance1 = parseInt(playerDistanceList[serverSitNum1][serverSitNum2]);
        var distance2 = parseInt(playerDistanceList[serverSitNum2][serverSitNum1]);
        return distance1>distance2 ? distance1:distance2;
    }

});