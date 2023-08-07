import os,shutil,tqdm
import numpy as np
import cv2,json,base64
import matplotlib.pyplot as plt

def mask2color(
                img=False,
                mask_list=False,
                mask_names=False,
                dyeing_rate=False,
                colormap=False):
        '''
        將mask轉成彩色並和原圖進行疊合\n
        @input\n
        `img`:彩色原圖\n
        `mask_list`:list中放入所有的mask ex:[mask1,mask2,...]\n
        `mask_names`:mask依序的名稱 ex:[mask1,mask2,...] \n
        `dyeing_rate`:染色程度,0~1,越大代表顏色越明顯 ex:0.5 \n
        `colormap`:每個對應mask要染的顏色,依照順序 ex:[[255,0,0],[0,255,0],[0,0,255],[125,0,125],[125,125,0]]\n
        @output \n
        `concate_mask`:以axis=1 concate好所有的染色mask array\n
        '''

        #assert img,'請輸入原圖'
        #assert mask_list,'請輸入mask的list'
        assert dyeing_rate,'請輸入染色程度0~1'
        assert colormap,'請輸入mask要上的顏色'
        

        #傳入的mask數量和個別要染的顏色對不起來
        if len(mask_list) > len(colormap):
            raise 'mask數量和colormap數量不一致'
        
        divider = np.empty((img.shape[0], 2), dtype='uint8')
        divider.fill(255)
        divider = cv2.cvtColor(divider, cv2.COLOR_GRAY2BGR)
        
        return_mask = [img,divider]

        #個別mask染色結果
        for index in range(len(mask_list)):
            mask_value = mask_list[index]
            #如果mask數值>1代表為0~255 要做normalize 0~1
            if mask_value.max()>1:
                mask_value = mask_list[index]/255
            #製作mask_RGB_channel 3channel的RGB
            mask_RGB_channel = np.zeros([mask_list[index].shape[0], mask_list[index].shape[1], 3], dtype='uint8')
            fillColor = colormap[index]
            fillColor_index = [idx for idx,value in enumerate(fillColor) if value !=0 ]
            for color_channel in fillColor_index:
                mask_RGB_channel[:,:,color_channel] = fillColor[color_channel] * mask_value
                if mask_names:
                    cv2.putText(mask_RGB_channel,
                                mask_names[index],
                                (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2, cv2.LINE_AA
                    )
            return_mask.append(mask_RGB_channel)
            return_mask.append(divider)


        #單張綜合mask染色結果
        RGB_channel = np.zeros([mask_list[index].shape[0], mask_list[index].shape[1], 3], dtype='uint8')
        for index in range(len(mask_list)):
            mask_value = mask_list[index]/255
            fillColor = colormap[index]
            fillColor_index = [idx for idx,value in enumerate(fillColor) if value !=0 ]
            for color_channel in fillColor_index:
                RGB_channel[:,:,color_channel] = RGB_channel[:,:,color_channel]  + fillColor[color_channel] * mask_value
        #找到最大和最小值後 把數值壓到0~1以內
        RGB_channel = (RGB_channel/(RGB_channel.max()-RGB_channel.min()))*255
        
        #return_mask.append(RGB_channel)#所有染色mask合成一張
        #return_mask.append(divider)
        
        #原圖和mask染色疊合img + RGB_channel*dyeing_rate(染色程度)
        img_conc_mask = (img + 
                            RGB_channel*dyeing_rate)
        img_conc_mask = (img_conc_mask/(img_conc_mask.max()-img_conc_mask.min()))*255
        cv2.putText(img_conc_mask,
                                'merge',
                                (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2, cv2.LINE_AA
                    )

        #return_mask.append(img_conc_mask)
        #return_mask.append(divider)
        return_mask.insert(1,img_conc_mask)
        return_mask.insert(1,divider)

        concate_mask = np.concatenate(return_mask[:],axis=1)

        return concate_mask


if __name__ == "__main__":
    '''
    目前提供最多5種masks
    mask須為.png or .jpg
    '''

    images_path = f'./mask_merge/images/'
    masks_path = f'./mask_merge/masks/'
    result_path = f'./mask_merge/result/'

    try:
        shutil.rmtree(result_path)
    except:
        pass
    os.makedirs(result_path)

    dyeing_rate = 0.5
    masks_name = os.listdir(masks_path)
    masks_name_num = len(masks_name)
    colormap = [[0,255,0],[255,0,0],[255,125,0],[0,0,255]]
    colormap = colormap[:len(masks_name)]

    for img_name in tqdm.tqdm(os.listdir(images_path)):
        img_title = img_name.split('.')[0]
        img = cv2.imread(f'{images_path}/{img_name}')
 
        masks_img = []
        for mask_name in masks_name:
            try:
                mask = cv2.imread(f'{masks_path}/{mask_name}/{img_title}.png',0)
            except:
                mask = cv2.imread(f'{masks_path}/{mask_name}/{img_title}.jpg',0)
            masks_img.append(mask)
        
        con = mask2color(img=img,
                         mask_list=masks_img,
                         mask_names=masks_name,
                         dyeing_rate=dyeing_rate,
                         colormap = colormap)
        
        cv2.imwrite(f'{result_path}/{img_title}.jpg',con)
