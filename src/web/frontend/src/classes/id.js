class ID {
    constructor(id = null) {
        if (id === null) {
            this.objID = this.rawID = ID.idCount;
            this.isDiscordID = false;
        } else {
            this.rawID = id;
            this.objID = ID.idCount;
            this.isDiscordID = true;
        }
        ID.idCount++;
    }
    setID(id) {
        this.rawID = id;
        this.isDiscordID = true;
    }
    copy() {
        const clone = new ID(this.rawID);
        clone.isDiscordID = this.isDiscordID;
        clone.objID = this.objID;
        return clone;
    }
}
ID.idCount = 0;

export default ID;